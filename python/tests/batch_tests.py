import os
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from cgm_file import convert_binary_to_cleartext
from cleartextcgm_to_svg import CGMToSVGConverter
from svg_to_pdf import SVGToPDFConverter

for fname in os.listdir('python/tests/batch_tests'):
    if fname.lower().endswith('.cgm') and "_cleartext" in fname:
        os.remove(os.path.join('python/tests/batch_tests', fname))
    if fname.lower().endswith('.svg'):
        os.remove(os.path.join('python/tests/batch_tests', fname))
    if fname.lower().endswith('.pdf'):
        os.remove(os.path.join('python/tests/batch_tests', fname))

for cgm in os.listdir('python/tests/batch_tests'):
    if cgm.lower().endswith('.cgm'):
        base_name = os.path.splitext(cgm)[0]
        output_txt = base_name + '_cleartext.cgm'
        print(f'Converting {cgm} to {output_txt}...')
        convert_binary_to_cleartext(
            os.path.join('python/tests/batch_tests', cgm),
            os.path.join('python/tests/batch_tests', output_txt)
        )

        svg_converter = CGMToSVGConverter()

        svg_converter.convert_file(
            os.path.join('python/tests/batch_tests', output_txt),
            os.path.join('python/tests/batch_tests', base_name + '.svg')
        )
        print(f'Converted {cgm} to SVG as {base_name + ".svg"}')

        pdf_converter = SVGToPDFConverter()
        pdf_converter.convert_svg_to_pdf(
            os.path.join('python/tests/batch_tests', base_name + '.svg'),
            os.path.join('python/tests/batch_tests', base_name + '.pdf')
        )
        print(f'Converted {base_name + ".svg"} to PDF as {base_name + ".pdf"}')

unknown_commands = {}
total_unknown = 0
for cgm in os.listdir('python/tests/batch_tests'):
    if cgm.lower().endswith('.cgm'):
        if "_cleartext" in cgm:
            try:
                with open(os.path.join('python/tests/batch_tests', cgm), 'r', encoding='utf-8') as f:
                    content = f.read()
                    count = content.count('Unknown command')
                    total_unknown += count
            except UnicodeDecodeError:
                # Try with latin-1 encoding for files with binary data
                try:
                    with open(os.path.join('python/tests/batch_tests', cgm), 'r', encoding='latin-1') as f:
                        content = f.read()
                        count = content.count('Unknown command')
                        total_unknown += count
                        print(f"  Warning: {cgm} contains binary data, used latin-1 encoding")
                except Exception as e:
                    print(f"  Error reading {cgm}: {e}")
                    count = 0
            unknown_commands[cgm] = count

print("\nSummary of Unknown Commands:")
for fname, count in unknown_commands.items():
    print(f"  {fname}: {count} unknown commands")
print(f"\nTotal unknown commands across all files: {total_unknown}")