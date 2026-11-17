/**
 * Fails if the publicly served asset_dir (build/) holds source maps or
 * references them. Run after a production build; `npm run dev` emits maps on
 * purpose and must never be packaged.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const buildDir = fileURLToPath(new URL("../build", import.meta.url));

function* files(dir: string): Generator<string> {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) yield* files(path);
    else yield path;
  }
}

const problems: string[] = [];
for (const path of files(buildDir)) {
  if (path.endsWith(".map")) problems.push(`source map: ${path}`);
  else if (readFileSync(path, "utf8").includes("sourceMappingURL=")) {
    problems.push(`source map reference: ${path}`);
  }
}

if (problems.length > 0) {
  console.error(problems.join("\n"));
  process.exit(1);
}
console.log("build/ has no source maps");
