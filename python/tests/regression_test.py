#!/usr/bin/env python3
"""
CGM Regression Test Suite

This test creates a baseline of converted files and compares new conversions
against the baseline to detect any regressions.

Usage:
    python regression_test.py --create-baseline    # Create baseline from current output
    python regression_test.py --test                # Run regression test against baseline
    python regression_test.py --report              # Generate detailed comparison report
"""

import os
import sys
import shutil
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import difflib
import re


class RegressionTester:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.batch_tests_dir = workspace_root / "tests" / "batch_tests"
        self.baseline_dir = workspace_root / "tests" / "baseline"
        self.regression_dir = workspace_root / "tests" / "regression_output"
        self.report_dir = workspace_root / "tests" / "regression_reports"
        self.converter_script = workspace_root / "cleartextcgm_to_svg.py"
        self.binary_converter = workspace_root / "main.py"  # Python binary-to-cleartext converter
        
    def create_baseline(self) -> bool:
        """Create baseline by copying current batch_tests output"""
        print("=" * 80)
        print("CREATING BASELINE")
        print("=" * 80)
        
        # Create baseline directory
        if self.baseline_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.baseline_dir.parent / f"baseline_backup_{timestamp}"
            print(f"\nBacking up existing baseline to: {backup_dir}")
            shutil.move(str(self.baseline_dir), str(backup_dir))
        
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all cleartext CGM files
        cleartext_files = list(self.batch_tests_dir.glob("*_cleartext.cgm"))
        print(f"\nCopying {len(cleartext_files)} cleartext CGM files...")
        for src in cleartext_files:
            dst = self.baseline_dir / src.name
            shutil.copy2(src, dst)
            print(f"  ✓ {src.name}")
        
        # Copy all SVG files
        svg_files = list(self.batch_tests_dir.glob("*.svg"))
        print(f"\nCopying {len(svg_files)} SVG files...")
        for src in svg_files:
            dst = self.baseline_dir / src.name
            shutil.copy2(src, dst)
            print(f"  ✓ {src.name}")
        
        # Create metadata file
        metadata = {
            "created": datetime.now().isoformat(),
            "cleartext_files": len(cleartext_files),
            "svg_files": len(svg_files),
            "files": [f.name for f in cleartext_files + svg_files]
        }
        
        metadata_file = self.baseline_dir / "baseline_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Baseline created successfully at: {self.baseline_dir}")
        print(f"  - {len(cleartext_files)} cleartext CGM files")
        print(f"  - {len(svg_files)} SVG files")
        
        return True
    
    def convert_binary_to_cleartext(self, binary_cgm: Path, output_dir: Path) -> Path:
        """Convert binary CGM to cleartext using Python converter"""
        cleartext_name = binary_cgm.stem + "_cleartext.cgm"
        cleartext_path = output_dir / cleartext_name
        
        if not self.binary_converter.exists():
            raise FileNotFoundError(f"Binary converter not found at {self.binary_converter}")
        
        cmd = ["python3", str(self.binary_converter), str(binary_cgm), str(cleartext_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.workspace_root))
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to convert {binary_cgm.name}: {result.stderr}")
        
        return cleartext_path
    
    def convert_cleartext_to_svg(self, cleartext_cgm: Path, output_dir: Path) -> Path:
        """Convert cleartext CGM to SVG using Python converter"""
        svg_name = cleartext_cgm.stem.replace("_cleartext", "") + ".svg"
        svg_path = output_dir / svg_name
        
        cmd = ["python3", str(self.converter_script), str(cleartext_cgm), str(svg_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.workspace_root))
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to convert {cleartext_cgm.name}: {result.stderr}")
        
        return svg_path
    
    def run_regression_test(self) -> Dict:
        """Run full regression test: convert all files and compare with baseline"""
        print("=" * 80)
        print("RUNNING REGRESSION TEST")
        print("=" * 80)
        
        if not self.baseline_dir.exists():
            print("\n❌ ERROR: No baseline found. Please run with --create-baseline first.")
            return {}
        
        # Create regression output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.regression_dir / f"run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nOutput directory: {run_dir}")
        
        # Find all binary CGM files
        binary_cgm_files = [f for f in self.batch_tests_dir.glob("*.CGM") 
                           if not f.name.endswith("_cleartext.cgm")]
        
        print(f"\nFound {len(binary_cgm_files)} binary CGM files to process")
        
        results = {
            "timestamp": timestamp,
            "total_files": len(binary_cgm_files),
            "conversions": {},
            "comparisons": {}
        }
        
        # Process each file
        for i, binary_cgm in enumerate(binary_cgm_files, 1):
            print(f"\n[{i}/{len(binary_cgm_files)}] Processing {binary_cgm.name}...")
            
            try:
                # Convert binary → cleartext
                print(f"  Converting to cleartext...")
                cleartext_path = self.convert_binary_to_cleartext(binary_cgm, run_dir)
                print(f"  ✓ Created {cleartext_path.name}")
                
                # Convert cleartext → SVG
                print(f"  Converting to SVG...")
                svg_path = self.convert_cleartext_to_svg(cleartext_path, run_dir)
                print(f"  ✓ Created {svg_path.name}")
                
                results["conversions"][binary_cgm.name] = {
                    "status": "success",
                    "cleartext": cleartext_path.name,
                    "svg": svg_path.name
                }
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results["conversions"][binary_cgm.name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Compare with baseline
        print("\n" + "=" * 80)
        print("COMPARING WITH BASELINE")
        print("=" * 80)
        
        self._compare_with_baseline(run_dir, results)
        
        # Save results
        results_file = run_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to: {results_file}")
        
        return results
    
    def _compare_with_baseline(self, run_dir: Path, results: Dict):
        """Compare generated files with baseline"""
        
        # Compare cleartext files
        print("\nComparing cleartext CGM files...")
        cleartext_diffs = self._compare_files(
            run_dir.glob("*_cleartext.cgm"),
            self.baseline_dir,
            "cleartext"
        )
        results["comparisons"]["cleartext"] = cleartext_diffs
        
        # Compare SVG files
        print("\nComparing SVG files...")
        svg_diffs = self._compare_files(
            run_dir.glob("*.svg"),
            self.baseline_dir,
            "svg"
        )
        results["comparisons"]["svg"] = svg_diffs
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPARISON SUMMARY")
        print("=" * 80)
        
        for file_type, diffs in [("Cleartext CGM", cleartext_diffs), ("SVG", svg_diffs)]:
            total = len(diffs)
            identical = sum(1 for d in diffs.values() if d["status"] == "identical")
            different = sum(1 for d in diffs.values() if d["status"] == "different")
            missing = sum(1 for d in diffs.values() if d["status"] == "missing_baseline")
            
            print(f"\n{file_type} files:")
            print(f"  Total: {total}")
            print(f"  ✓ Identical: {identical}")
            if different > 0:
                print(f"  ⚠ Different: {different}")
            if missing > 0:
                print(f"  ⚠ Missing in baseline: {missing}")
    
    def _compare_files(self, new_files: List[Path], baseline_dir: Path, 
                      file_type: str) -> Dict:
        """Compare files with baseline and return diff information"""
        diffs = {}
        
        for new_file in new_files:
            baseline_file = baseline_dir / new_file.name
            
            if not baseline_file.exists():
                diffs[new_file.name] = {
                    "status": "missing_baseline",
                    "message": "No baseline file for comparison"
                }
                print(f"  ⚠ {new_file.name}: No baseline")
                continue
            
            # Read files
            with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                new_content = f.read()
            with open(baseline_file, 'r', encoding='utf-8', errors='ignore') as f:
                baseline_content = f.read()
            
            # Compare
            if new_content == baseline_content:
                diffs[new_file.name] = {
                    "status": "identical",
                    "message": "Files are identical"
                }
                print(f"  ✓ {new_file.name}: Identical")
            else:
                # Calculate diff statistics
                new_lines = new_content.splitlines()
                baseline_lines = baseline_content.splitlines()
                
                diff = list(difflib.unified_diff(
                    baseline_lines, new_lines,
                    fromfile=f"baseline/{new_file.name}",
                    tofile=f"new/{new_file.name}",
                    lineterm=''
                ))
                
                added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
                removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
                
                diffs[new_file.name] = {
                    "status": "different",
                    "lines_added": added,
                    "lines_removed": removed,
                    "total_changes": added + removed,
                    "size_new": len(new_content),
                    "size_baseline": len(baseline_content)
                }
                print(f"  ⚠ {new_file.name}: Different (+{added}/-{removed} lines)")
        
        return diffs
    
    def generate_detailed_report(self, results_file: Path = None):
        """Generate detailed HTML report from test results"""
        print("=" * 80)
        print("GENERATING DETAILED REPORT")
        print("=" * 80)
        
        if results_file is None:
            # Find most recent results
            if not self.regression_dir.exists():
                print("\n❌ No regression test results found")
                return
            
            run_dirs = sorted(self.regression_dir.glob("run_*"), reverse=True)
            if not run_dirs:
                print("\n❌ No regression test results found")
                return
            
            results_file = run_dirs[0] / "test_results.json"
        
        if not results_file.exists():
            print(f"\n❌ Results file not found: {results_file}")
            return
        
        # Load results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Create report
        self.report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = results["timestamp"]
        report_file = self.report_dir / f"report_{timestamp}.html"
        
        html = self._generate_html_report(results, results_file.parent)
        
        with open(report_file, 'w') as f:
            f.write(html)
        
        print(f"\n✓ Report generated: {report_file}")
        
        # Also create a text summary
        summary_file = self.report_dir / f"summary_{timestamp}.txt"
        summary = self._generate_text_summary(results)
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"✓ Summary generated: {summary_file}")
    
    def _generate_html_report(self, results: Dict, run_dir: Path) -> str:
        """Generate HTML report"""
        timestamp = results["timestamp"]
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CGM Regression Test Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .summary-item {{ background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
        .summary-item strong {{ display: block; color: #666; font-size: 0.9em; }}
        .summary-item span {{ font-size: 1.5em; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .status-identical {{ color: #4CAF50; font-weight: bold; }}
        .status-different {{ color: #ff9800; font-weight: bold; }}
        .status-missing {{ color: #f44336; font-weight: bold; }}
        .status-failed {{ color: #f44336; font-weight: bold; }}
        .diff-info {{ font-size: 0.9em; color: #666; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CGM Regression Test Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p class="timestamp">Test Run: {timestamp}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <strong>Total Files</strong>
                    <span>{results["total_files"]}</span>
                </div>
"""
        
        # Add conversion summary
        conversions = results.get("conversions", {})
        successful = sum(1 for c in conversions.values() if c.get("status") == "success")
        failed = sum(1 for c in conversions.values() if c.get("status") == "failed")
        
        html += f"""
                <div class="summary-item">
                    <strong>Successful Conversions</strong>
                    <span style="color: #4CAF50;">{successful}</span>
                </div>
                <div class="summary-item">
                    <strong>Failed Conversions</strong>
                    <span style="color: #f44336;">{failed}</span>
                </div>
"""
        
        # Add comparison summary
        for file_type in ["cleartext", "svg"]:
            if file_type in results.get("comparisons", {}):
                diffs = results["comparisons"][file_type]
                identical = sum(1 for d in diffs.values() if d["status"] == "identical")
                different = sum(1 for d in diffs.values() if d["status"] == "different")
                
                html += f"""
                <div class="summary-item">
                    <strong>{file_type.upper()} Identical</strong>
                    <span style="color: #4CAF50;">{identical}</span>
                </div>
                <div class="summary-item">
                    <strong>{file_type.upper()} Different</strong>
                    <span style="color: #ff9800;">{different}</span>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <h2>Conversion Results</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Status</th>
                <th>Cleartext</th>
                <th>SVG</th>
            </tr>
"""
        
        for filename, conv in sorted(conversions.items()):
            status = conv.get("status", "unknown")
            status_class = f"status-{status}"
            
            cleartext = conv.get("cleartext", "-")
            svg = conv.get("svg", "-")
            
            html += f"""
            <tr>
                <td>{filename}</td>
                <td class="{status_class}">{status.upper()}</td>
                <td>{cleartext}</td>
                <td>{svg}</td>
            </tr>
"""
        
        html += """
        </table>
"""
        
        # Add comparison tables
        for file_type, title in [("cleartext", "Cleartext CGM"), ("svg", "SVG")]:
            if file_type not in results.get("comparisons", {}):
                continue
            
            html += f"""
        <h2>{title} File Comparison</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
"""
            
            diffs = results["comparisons"][file_type]
            for filename, diff in sorted(diffs.items()):
                status = diff["status"]
                status_class = f"status-{status}"
                
                if status == "identical":
                    details = "No differences"
                elif status == "different":
                    added = diff.get("lines_added", 0)
                    removed = diff.get("lines_removed", 0)
                    details = f"+{added} / -{removed} lines"
                else:
                    details = diff.get("message", "-")
                
                html += f"""
            <tr>
                <td>{filename}</td>
                <td class="{status_class}">{status.upper()}</td>
                <td class="diff-info">{details}</td>
            </tr>
"""
            
            html += """
        </table>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_text_summary(self, results: Dict) -> str:
        """Generate text summary report"""
        timestamp = results["timestamp"]
        
        summary = f"""
CGM REGRESSION TEST SUMMARY
{'=' * 80}
Test Run: {timestamp}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

OVERVIEW
{'-' * 80}
Total Files: {results["total_files"]}
"""
        
        # Conversion summary
        conversions = results.get("conversions", {})
        successful = sum(1 for c in conversions.values() if c.get("status") == "success")
        failed = sum(1 for c in conversions.values() if c.get("status") == "failed")
        
        summary += f"""
CONVERSIONS
{'-' * 80}
Successful: {successful}
Failed: {failed}
"""
        
        # Comparison summary
        for file_type, title in [("cleartext", "CLEARTEXT CGM"), ("svg", "SVG")]:
            if file_type not in results.get("comparisons", {}):
                continue
            
            diffs = results["comparisons"][file_type]
            identical = sum(1 for d in diffs.values() if d["status"] == "identical")
            different = sum(1 for d in diffs.values() if d["status"] == "different")
            missing = sum(1 for d in diffs.values() if d["status"] == "missing_baseline")
            
            summary += f"""
{title} COMPARISON
{'-' * 80}
Total: {len(diffs)}
Identical: {identical}
Different: {different}
Missing in baseline: {missing}
"""
            
            # List different files
            if different > 0:
                summary += f"\nFiles with differences:\n"
                for filename, diff in sorted(diffs.items()):
                    if diff["status"] == "different":
                        added = diff.get("lines_added", 0)
                        removed = diff.get("lines_removed", 0)
                        summary += f"  - {filename}: +{added}/-{removed} lines\n"
        
        return summary


def main():
    parser = argparse.ArgumentParser(
        description="CGM Regression Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create baseline from current output
  python regression_test.py --create-baseline

  # Run regression test
  python regression_test.py --test

  # Generate report from most recent test
  python regression_test.py --report

  # Do everything: test and report
  python regression_test.py --test --report
"""
    )
    
    parser.add_argument(
        '--create-baseline',
        action='store_true',
        help='Create baseline from current batch_tests output'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run regression test against baseline'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report from test results'
    )
    
    args = parser.parse_args()
    
    # Determine workspace root (parent of this script)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    
    tester = RegressionTester(workspace_root)
    
    if args.create_baseline:
        tester.create_baseline()
    
    if args.test:
        results = tester.run_regression_test()
        
        if args.report and results:
            timestamp = results["timestamp"]
            results_file = tester.regression_dir / f"run_{timestamp}" / "test_results.json"
            tester.generate_detailed_report(results_file)
    elif args.report:
        tester.generate_detailed_report()
    
    if not (args.create_baseline or args.test or args.report):
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
