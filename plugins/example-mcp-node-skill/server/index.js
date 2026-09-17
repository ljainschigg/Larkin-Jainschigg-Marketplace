import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import figlet from "figlet";

const server = new Server(
  { name: "hello-node", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "hello_node",
      description: "Says hello using Node.js and figlet ASCII art.",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Name to greet" },
        },
        required: ["name"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name } = request.params.arguments;
  const art = figlet.textSync(`Hello, ${name}!`);
  return {
    content: [{ type: "text", text: art }],
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
