/**
 * Compile all three registry contracts from the current checkout.
 *
 * The output overwrites the local backend ABI/bytecode artifacts. This script
 * intentionally runs in CI before the Ganache test, so a stale committed ABI
 * cannot silently mask changes to the Solidity source.
 *
 * Run: npm install --no-save solc@0.8.20
 *      node scripts/compile-contract-artifacts.mjs
 */
import { createHash } from "node:crypto";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import solc from "solc";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const CONTRACT_NAMES = ["CredentialRegistry", "GroupRegistry", "ContributionRegistry"];
const EXPECTED_COMPILER = "0.8.20";

if (!solc.version().startsWith(EXPECTED_COMPILER + "+")) {
  throw new Error(`Incorrect Solidity compiler: ${solc.version()}, expected ${EXPECTED_COMPILER}`);
}

const sources = {};
for (const name of CONTRACT_NAMES) {
  const sourcePath = `smart_contracts/contracts/${name}.sol`;
  sources[sourcePath] = {
    content: readFileSync(resolve(ROOT, sourcePath), "utf8"),
  };
}

const compiled = JSON.parse(solc.compile(JSON.stringify({
  language: "Solidity",
  sources,
  settings: {
    evmVersion: "istanbul",
    optimizer: { enabled: false, runs: 200 },
    outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } },
  },
})));

for (const diagnostic of compiled.errors ?? []) {
  if (diagnostic.severity === "error") {
    throw new Error(`Solidity compilation failed: ${diagnostic.formattedMessage}`);
  }
}

const artifactDirectory = resolve(ROOT, "blockchain", "abi");
mkdirSync(artifactDirectory, { recursive: true });

for (const name of CONTRACT_NAMES) {
  const sourcePath = `smart_contracts/contracts/${name}.sol`;
  const contract = compiled.contracts?.[sourcePath]?.[name];
  if (!contract?.abi?.length || !contract.evm?.bytecode?.object) {
    throw new Error(`Missing ABI or bytecode for ${name}`);
  }

  const sha256 = createHash("sha256")
    .update(sources[sourcePath].content, "utf8")
    .digest("hex");

  const artifact = {
    contractName: name,
    compilerVersion: solc.version(),
    sourceSha256: sha256,
    abi: contract.abi,
    bytecode: `0x${contract.evm.bytecode.object}`,
  };

  const dest = resolve(artifactDirectory, `${name}.json`);
  writeFileSync(dest, JSON.stringify(artifact, null, 2) + "\n", "utf8");
  process.stdout.write(`COMPILED_CONTRACT name=${name} source_sha256=${sha256} compiler=${solc.version()}\n`);
}
