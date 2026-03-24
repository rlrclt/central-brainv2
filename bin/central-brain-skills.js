#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const skillsRoot = path.join(repoRoot, "skills");

const TARGETS = {
  codex: {
    label: "Codex",
    root: path.join(os.homedir(), ".codex"),
    skillsDir: path.join(os.homedir(), ".codex", "skills")
  },
  claude: {
    label: "Claude",
    root: path.join(os.homedir(), ".claude"),
    skillsDir: path.join(os.homedir(), ".claude", "skills")
  },
  gemini: {
    label: "Gemini",
    root: path.join(os.homedir(), ".gemini"),
    skillsDir: path.join(os.homedir(), ".gemini", "skills")
  }
};

function printHelp() {
  console.log(`Central Brain Skills

Usage:
  brain-skills list
  brain-skills list-targets
  brain-skills status
  brain-skills install -g -y
  brain-skills install --target codex,claude,gemini --skill brain-start
  brain-skills install --dest PATH --skill brain-start

Notes:
  - install -g installs into supported AI folders under ~/.codex, ~/.claude, ~/.gemini
  - -y skips overwrite prompts
  - --target accepts a comma-separated list
  - --dest installs to one explicit path instead of AI-specific folders
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
    dest: null,
    targets: []
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
      args.dest = argv[i + 1] || null;
      i += 1;
    } else if (token === "--target" || token === "--targets") {
      args.targets = (argv[i + 1] || "")
        .split(",")
        .map((value) => value.trim().toLowerCase())
        .filter(Boolean);
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

function resolveTargets(args) {
  if (args.dest) {
    return [{ key: "custom", label: "Custom", skillsDir: args.dest, root: path.dirname(args.dest) }];
  }

  const requested = args.targets.length > 0 ? args.targets : (args.global ? Object.keys(TARGETS) : ["codex"]);
  return requested.map((name) => {
    if (!TARGETS[name]) {
      throw new Error(`Unknown target: ${name}`);
    }
    return { key: name, ...TARGETS[name] };
  });
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
  return target;
}

function printAvailableSkills(skills) {
  if (skills.length === 0) {
    console.log("No skills bundled in this package.");
    return;
  }

  console.log("Available Central Brain skills:");
  for (const skill of skills) {
    console.log(`- ${skill}`);
  }
}

function printTargets() {
  console.log("Supported AI targets:");
  for (const [key, target] of Object.entries(TARGETS)) {
    console.log(`- ${key}: ${target.skillsDir}`);
  }
}

function targetStatus(skills) {
  console.log("Central Brain skill status:");
  for (const [key, target] of Object.entries(TARGETS)) {
    const rootExists = fs.existsSync(target.root);
    const installedSkills = skills.filter((skill) => fs.existsSync(path.join(target.skillsDir, skill)));
    const installedText = installedSkills.length > 0 ? installedSkills.join(", ") : "none";
    console.log(`- ${key} (${target.label})`);
    console.log(`  root: ${target.root} ${rootExists ? "[present]" : "[missing]"}`);
    console.log(`  skills: ${target.skillsDir}`);
    console.log(`  installed: ${installedText}`);
  }
}

function installForTargets(skillNames, targets, yes) {
  const results = [];

  for (const target of targets) {
    ensureDir(target.skillsDir);
    for (const skillName of skillNames) {
      const installedPath = installSkill(skillName, target.skillsDir, yes);
      results.push({
        target: target.key,
        label: target.label,
        skill: skillName,
        path: installedPath
      });
    }
  }

  return results;
}

function printInstallResults(results) {
  for (const item of results) {
    console.log(`Installed ${item.skill} for ${item.label} -> ${item.path}`);
  }
  console.log("Done. Restart your AI tools if they cache installed skills.");
}

function main() {
  const args = parseArgs(process.argv);
  const skills = getSkillNames();

  if (args.command === "help" || args.command === "--help" || args.command === "-h") {
    printHelp();
    return;
  }

  if (args.command === "list") {
    printAvailableSkills(skills);
    return;
  }

  if (args.command === "list-targets") {
    printTargets();
    return;
  }

  if (args.command === "status") {
    targetStatus(skills);
    return;
  }

  if (args.command === "install") {
    if (skills.length === 0) {
      throw new Error("No installable skills found in this package.");
    }

    const skillNames = args.skill ? [args.skill] : skills;
    const targets = resolveTargets(args);
    const results = installForTargets(skillNames, targets, args.yes);
    printInstallResults(results);
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
