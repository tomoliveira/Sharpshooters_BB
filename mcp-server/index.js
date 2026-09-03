#!/usr/bin/env node
// Local stdio MCP server for the Sharpshooters_BB report database.
//
// This does NOT talk to BuzzerBeater directly - it reads the same report.db
// that docs/index.html reads client-side, fetched from wherever GitHub Pages
// is serving this repo (REPORT_DB_URL, default below). The daily GitHub
// Actions job is what keeps that file fresh; this server just gives Claude
// (or any other MCP client) structured tool access to its contents instead
// of having to scrape the rendered HTML.
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema, CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import initSqlJs from "sql.js";

const DB_URL = process.env.REPORT_DB_URL || "https://tomoliveira.github.io/Sharpshooters_BB/report.db";
const DEFAULT_TEAM_KEY = process.env.DEFAULT_TEAM_KEY || "sharpshooters";
const CACHE_MS = 5 * 60 * 1000; // report.db only changes once a day; 5min avoids refetching on every tool call in a burst

let SQL = null;
let cachedDb = null;
let cachedAt = 0;

async function getDb() {
  if (!SQL) SQL = await initSqlJs();
  const now = Date.now();
  if (cachedDb && now - cachedAt < CACHE_MS) return cachedDb;
  const resp = await fetch(DB_URL, { cache: "no-store" });
  if (!resp.ok) throw new Error(`Failed to fetch ${DB_URL}: HTTP ${resp.status}`);
  const buf = await resp.arrayBuffer();
  cachedDb = new SQL.Database(new Uint8Array(buf));
  cachedAt = now;
  return cachedDb;
}

function latestSnapshot(db, teamKey) {
  const res = db.exec(
    "SELECT data_json, fetched_at FROM snapshots WHERE team_key = ? ORDER BY fetched_at DESC LIMIT 1",
    [teamKey]
  );
  if (!res.length || !res[0].values.length) return null;
  const [dataJson, fetchedAt] = res[0].values[0];
  return { data: JSON.parse(dataJson), fetchedAt };
}

const TOOLS = [
  {
    name: "get_report_snapshot",
    description:
      "Get the latest full BuzzerBeater team report snapshot: team info, economy/finances, schedule, standings, roster + skills, staff, arena, investments ledger, and training-minutes status.",
    inputSchema: {
      type: "object",
      properties: {
        team_key: { type: "string", description: `Team key, e.g. '${DEFAULT_TEAM_KEY}'` },
      },
    },
  },
  {
    name: "get_report_section",
    description:
      "Get one top-level section of the latest report snapshot instead of the whole thing. Useful sections: 'team', 'economy', 'schedule', 'standings', 'roster', 'roster_skills', 'staff', 'training_cards', 'training_minutes', 'minutes_vs_money', 'arena_live', 'investments', 'division_rows'.",
    inputSchema: {
      type: "object",
      properties: {
        team_key: { type: "string", description: `Team key, e.g. '${DEFAULT_TEAM_KEY}'` },
        section: { type: "string", description: "Top-level key of the report data to return" },
      },
      required: ["section"],
    },
  },
  {
    name: "list_snapshots",
    description: "List the fetch timestamps of recent report snapshots for a team, newest first.",
    inputSchema: {
      type: "object",
      properties: {
        team_key: { type: "string", description: `Team key, e.g. '${DEFAULT_TEAM_KEY}'` },
        limit: { type: "number", description: "Max rows to return (default 10)" },
      },
    },
  },
];

const server = new Server(
  { name: "sharpshooters-bb", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args = {} } = req.params;
  const teamKey = args.team_key || DEFAULT_TEAM_KEY;

  try {
    const db = await getDb();

    if (name === "get_report_snapshot") {
      const snap = latestSnapshot(db, teamKey);
      if (!snap) return textResult(`No snapshot found for team '${teamKey}'.`);
      return textResult(JSON.stringify(snap, null, 2));
    }

    if (name === "get_report_section") {
      const snap = latestSnapshot(db, teamKey);
      if (!snap) return textResult(`No snapshot found for team '${teamKey}'.`);
      const section = snap.data[args.section];
      if (section === undefined) {
        return textResult(
          `No section '${args.section}'. Available sections: ${Object.keys(snap.data).join(", ")}`
        );
      }
      return textResult(JSON.stringify({ fetchedAt: snap.fetchedAt, [args.section]: section }, null, 2));
    }

    if (name === "list_snapshots") {
      const limit = args.limit || 10;
      const res = db.exec(
        "SELECT fetched_at FROM snapshots WHERE team_key = ? ORDER BY fetched_at DESC LIMIT ?",
        [teamKey, limit]
      );
      const rows = res.length ? res[0].values.map((v) => v[0]) : [];
      return textResult(JSON.stringify(rows, null, 2));
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (err) {
    return { content: [{ type: "text", text: `Error: ${err.message}` }], isError: true };
  }
});

function textResult(text) {
  return { content: [{ type: "text", text }] };
}

const transport = new StdioServerTransport();
await server.connect(transport);
