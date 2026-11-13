import { existsSync, readdirSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const local = process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python";
const python = process.env.PYTHON || (existsSync(local) ? local : "python");
function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error) { console.error(result.error.message); process.exit(1); }
  if (result.status !== 0) process.exit(result.status || 1);
}
run(python, ["-m", "ruff", "check", "boringnews", "tests", "scripts"]);
for (const dir of ["web", "functions", "tests", "scripts"]) {
  for (const file of readdirSync(dir)) {
    if (/\.(?:js|cjs|mjs)$/.test(file)) run(process.execPath, ["--check", join(dir, file)]);
  }
}
run(python, ["scripts/check_docs.py"]);
if (!process.argv.includes("--lint-only")) run(python, ["-m", "pytest", "-q"]);
