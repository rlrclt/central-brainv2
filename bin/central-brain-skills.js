#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const skillsRoot = path.join(repoRoot, "skills");

function printHelp() {
  console.log(`Central Brain Skills

Usage:
  central-brain-skills list
  central-brain-skills install [-g] [-y] [--skill brain-start] [--dest PATH]

Notes:
  - -g is accepted for compatibility and installs into ~/.codex/skills by default
  - -y skips overwrite prompts
  - If --skill is omitted, all bundled skills are installed
`);
}

function getSkillNames() {
  if (!fs.existsSync(skillsRoot)) {
    return [];
  }

  return fs.readdirSync(skillsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(skillsRoot, name, "SKILL.md")))
    .sort();
}

function parseArgs(argv) {
  const args = {
    command: argv[2] || "help",
    yes: false,
    global: false,
    skill: null,
    dest: path.join(os.homedir(), ".codex", "skills")
  };

  for (let i = 3; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "-y" || token === "--yes") {
      args.yes = true;
    } else if (token === "-g" || token === "--global") {
      args.global = true;
    } else if (token === "--skill") {
      args.skill = argv[i + 1] || null;
      i += 1;
    } else if (token === "--dest") {
      args.dest = argv[i + 1] || args.dest;
      i += 1;
    }
  }

  return args;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function copyDir(source, target) {
  fs.cpSync(source, target, { recursive: true, force: true });
}

function installSkill(skillName, destRoot, yes) {
  const source = path.join(skillsRoot, skillName);
  const target = path.join(destRoot, skillName);

  if (!fs.existsSync(source)) {
    throw new Error(`Skill not found: ${skillName}`);
  }

  if (fs.existsSync(target) && !yes) {
    throw new Error(`Skill already exists: ${target}. Re-run with -y to overwrite.`);
  }

  ensureDir(destRoot);
  copyDir(source, target);
  console.log(`Installed ${skillName} -> ${target}`);
}

function main() {
  const args = parseArgs(process.argv);
  const skills = getSkillNames();

  if (args.command === "help" || args.command === "--help" || args.command === "-h") {
    printHelp();
    return;
  }

  if (args.command === "list") {
    if (skills.length === 0) {
      console.log("No skills bundled in this package.");
      return;
    }

    console.log("Available Central Brain skills:");
    for (const skill of skills) {
      console.log(`- ${skill}`);
    }
    return;
  }

  if (args.command === "install") {
    if (skills.length === 0) {
      throw new Error("No installable skills found in this package.");
    }

    const targets = args.skill ? [args.skill] : skills;
    for (const skillName of targets) {
      installSkill(skillName, args.dest, args.yes);
    }

    console.log(`Done. Restart your AI tool if it caches installed skills.`);
    return;
  }

  throw new Error(`Unknown command: ${args.command}`);
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
