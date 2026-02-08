#!/usr/bin/env node
/**
 * Chapter Count Validation Script
 * HARD CONSTRAINT: EXACTLY 6 CHAPTERS
 *
 * Run: node scripts/validate-chapters.js
 * Called automatically before every build via package.json scripts.
 */

const fs = require('fs');
const path = require('path');

const DOCS_DIR = path.join(__dirname, '..', 'docs');
const EXPECTED_COUNT = 6;
const EXPECTED_CHAPTERS = [
  'ch01-intro-physical-ai.mdx',
  'ch02-ros2-fundamentals.mdx',
  'ch03-digital-twin.mdx',
  'ch04-isaac-platform.mdx',
  'ch05-vla.mdx',
  'ch06-capstone.mdx',
];

function validateChapters() {
  console.log('🔒 Validating chapter count (HARD CONSTRAINT: exactly 6)...\n');

  if (!fs.existsSync(DOCS_DIR)) {
    console.error('❌ ERROR: docs/ directory not found at', DOCS_DIR);
    process.exit(1);
  }

  const mdxFiles = fs
    .readdirSync(DOCS_DIR)
    .filter((f) => f.startsWith('ch') && f.endsWith('.mdx'))
    .sort();

  console.log(`Found ${mdxFiles.length} chapter file(s):`);
  mdxFiles.forEach((f) => console.log(`  ✓ ${f}`));

  // Check count
  if (mdxFiles.length !== EXPECTED_COUNT) {
    console.error(
      `\n❌ CHAPTER LOCK VIOLATION: Expected ${EXPECTED_COUNT} chapters, found ${mdxFiles.length}.`
    );
    console.error('The chapter list is locked. Do not add or remove chapters.');
    process.exit(1);
  }

  // Check exact file names
  const missing = EXPECTED_CHAPTERS.filter((f) => !mdxFiles.includes(f));
  const extra = mdxFiles.filter((f) => !EXPECTED_CHAPTERS.includes(f));

  if (missing.length > 0) {
    console.error(`\n❌ Missing chapters: ${missing.join(', ')}`);
    process.exit(1);
  }

  if (extra.length > 0) {
    console.error(`\n❌ Unexpected chapters: ${extra.join(', ')}`);
    console.error('Only the 6 locked chapters are allowed.');
    process.exit(1);
  }

  console.log(`\n✅ Chapter validation PASSED: Exactly ${EXPECTED_COUNT} chapters found.`);
}

validateChapters();
