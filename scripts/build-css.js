#!/usr/bin/env node

/**
 * CSS Build Script for Production
 * Minifies CSS files and creates optimized builds
 */

const fs = require('fs');
const path = require('path');

// Simple CSS minifier (for production, consider using a more robust solution like clean-css)
function minifyCSS(css) {
  return css
    // Remove comments
    .replace(/\/\*[\s\S]*?\*\//g, '')
    // Remove extra whitespace
    .replace(/\s+/g, ' ')
    // Remove whitespace around certain characters
    .replace(/\s*{\s*/g, '{')
    .replace(/;\s*/g, ';')
    .replace(/}\s*/g, '}')
    .replace(/:\s*/g, ':')
    .replace(/,\s*/g, ',')
    // Remove trailing semicolons
    .replace(/;}/g, '}')
    .trim();
}

function buildCSS() {
  const staticDir = path.join(__dirname, '..', 'static');
  const cssDir = path.join(staticDir, 'css');
  const sourceFile = path.join(cssDir, 'components.css');
  const minifiedFile = path.join(cssDir, 'components.min.css');

  try {
    // Read source CSS
    const sourceCSS = fs.readFileSync(sourceFile, 'utf8');
    
    // Minify CSS
    const minifiedCSS = minifyCSS(sourceCSS);
    
    // Write minified CSS
    fs.writeFileSync(minifiedFile, minifiedCSS);
    
    // Calculate compression ratio
    const originalSize = Buffer.byteLength(sourceCSS, 'utf8');
    const minifiedSize = Buffer.byteLength(minifiedCSS, 'utf8');
    const compressionRatio = ((originalSize - minifiedSize) / originalSize * 100).toFixed(1);
    
    console.log(`✅ CSS minification complete:`);
    console.log(`   Original: ${originalSize} bytes`);
    console.log(`   Minified: ${minifiedSize} bytes`);
    console.log(`   Savings: ${compressionRatio}%`);
    
  } catch (error) {
    console.error('❌ CSS minification failed:', error.message);
    process.exit(1);
  }
}

// Run build if called directly
if (require.main === module) {
  buildCSS();
}

module.exports = { buildCSS, minifyCSS };
