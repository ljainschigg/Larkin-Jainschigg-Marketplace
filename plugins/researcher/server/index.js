import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";
import https from "https";
import http from "http";
import { createRequire } from "module";

const require = createRequire(import.meta.url);

// ---------------------------------------------------------------------------
// Download
// ---------------------------------------------------------------------------

function downloadPdf(url, destPath, timeoutSecs) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destPath);
    const proto = url.startsWith("https") ? https : http;
    const timeoutMs = timeoutSecs * 1000;

    const request = proto.get(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
      },
    }, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        file.close();
        fs.unlinkSync(destPath);
        return downloadPdf(response.headers.location, destPath, timeoutSecs)
          .then(resolve).catch(reject);
      }
      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(destPath);
        return reject(new Error(`HTTP ${response.statusCode} for ${url}`));
      }
      const contentType = response.headers["content-type"] || "";
      if (!contentType.includes("pdf") && !contentType.includes("octet-stream")) {
        console.error(`Warning: Content-Type is "${contentType}" — proceeding anyway`);
      }
      response.pipe(file);
      file.on("finish", () => file.close(resolve));
      file.on("error", (err) => { fs.unlinkSync(destPath); reject(err); });
    });

    request.setTimeout(timeoutMs, () => {
      request.destroy();
      reject(new Error(`Download timed out after ${timeoutSecs}s`));
    });
    request.on("error", (err) => {
      if (fs.existsSync(destPath)) fs.unlinkSync(destPath);
      reject(err);
    });
  });
}

// ---------------------------------------------------------------------------
// Text extraction
// ---------------------------------------------------------------------------

async function extractWithPdfParse(pdfPath) {
  const pdfParse = require("pdf-parse");
  const dataBuffer = fs.readFileSync(pdfPath);
  const data = await pdfParse(dataBuffer);
  return { text: data.text, pageCount: data.numpages, method: "pdf-parse" };
}

async function extractWithOcr(pdfPath) {
  const { createWorker } = require("tesseract.js");
  const worker = await createWorker("eng", 1, {
    logger: (m) => {
      if (m.status === "recognizing text") {
        process.stderr.write(`\rOCR progress: ${(m.progress * 100).toFixed(0)}%`);
      }
    },
  });
  const { data: { text } } = await worker.recognize(pdfPath);
  await worker.terminate();
  process.stderr.write("\n");
  return { text, pageCount: null, method: "tesseract-ocr" };
}

function writeTextFile(txtPath, text, meta) {
  const header = [
    `Source PDF: ${meta.sourceUrl || meta.localPath}`,
    `Local PDF:  ${meta.localPath}`,
    `Retrieved:  ${meta.retrievedAt}`,
    meta.pageCount ? `Pages:      ${meta.pageCount}` : null,
    `Extracted:  ${meta.method}`,
    "",
    "",
  ].filter(line => line !== null).join("\n");
  fs.writeFileSync(txtPath, header + text, "utf8");
}

// ---------------------------------------------------------------------------
// Core extract_pdf logic
// ---------------------------------------------------------------------------

async function extractPdf({ source, outdir, pdfName, extractOnly, timeout }) {
  const timeoutSecs = timeout || 60;
  const isUrl = source.startsWith("http://") || source.startsWith("https://");

  fs.mkdirSync(outdir, { recursive: true });

  let pdfPath;
  let sourceUrl = null;

  if (extractOnly) {
    pdfPath = path.resolve(source);
    if (!fs.existsSync(pdfPath)) throw new Error(`File not found: ${pdfPath}`);
  } else if (isUrl) {
    sourceUrl = source;
    const rawName = pdfName || path.basename(new URL(source).pathname) || "download.pdf";
    const safeName = rawName.endsWith(".pdf") ? rawName : rawName + ".pdf";
    pdfPath = path.join(outdir, safeName);
    await downloadPdf(source, pdfPath, timeoutSecs);
  } else {
    pdfPath = path.resolve(source);
    if (!fs.existsSync(pdfPath)) throw new Error(`File not found: ${pdfPath}`);
    if (path.dirname(pdfPath) !== path.resolve(outdir)) {
      const dest = path.join(outdir, pdfName || path.basename(pdfPath));
      fs.copyFileSync(pdfPath, dest);
      pdfPath = dest;
    }
  }

  const txtPath = pdfPath.replace(/\.pdf$/i, ".txt");

  let result;
  try {
    result = await extractWithPdfParse(pdfPath);
    const avgCharsPerPage = result.pageCount > 0
      ? result.text.trim().length / result.pageCount
      : result.text.trim().length;
    if (avgCharsPerPage < 80) {
      result = await extractWithOcr(pdfPath);
    }
  } catch (err) {
    result = await extractWithOcr(pdfPath);
  }

  const meta = {
    sourceUrl,
    localPath: pdfPath,
    retrievedAt: new Date().toISOString(),
    pageCount: result.pageCount,
    method: result.method,
  };
  writeTextFile(txtPath, result.text, meta);

  return {
    pdfPath,
    txtPath,
    method: result.method,
    pageCount: result.pageCount || null,
  };
}

// ---------------------------------------------------------------------------
// MCP server
// ---------------------------------------------------------------------------

const server = new Server(
  { name: "extract-pdf", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "extract_pdf",
    description: "Download a PDF from a URL (or use a local path) and extract its text. Falls back to OCR for image-only PDFs. Returns local paths to the saved .pdf and .txt files.",
    inputSchema: {
      type: "object",
      properties: {
        source: {
          type: "string",
          description: "URL or local file path of the PDF to process"
        },
        outdir: {
          type: "string",
          description: "Directory to save the PDF and extracted text files"
        },
        pdf_name: {
          type: "string",
          description: "Override the output filename (e.g. 'report.pdf'). Optional."
        },
        extract_only: {
          type: "boolean",
          description: "If true, skip download and extract from an existing local PDF. Optional."
        },
        timeout: {
          type: "number",
          description: "HTTP download timeout in seconds. Default: 60. Optional."
        }
      },
      required: ["source", "outdir"]
    }
  }]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "extract_pdf") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const { source, outdir, pdf_name, extract_only, timeout } = request.params.arguments;

  try {
    const result = await extractPdf({
      source,
      outdir,
      pdfName: pdf_name,
      extractOnly: extract_only || false,
      timeout: timeout || 60,
    });

    const summary = [
      `PDF saved:  ${result.pdfPath}`,
      `Text saved: ${result.txtPath}`,
      `Method:     ${result.method}`,
      result.pageCount ? `Pages:      ${result.pageCount}` : null,
    ].filter(Boolean).join("\n");

    return { content: [{ type: "text", text: summary }] };
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error: ${err.message}` }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
