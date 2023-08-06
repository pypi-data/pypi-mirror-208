import sys

from pii_transform.api.e2e import PiiTextProcessor

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <textfile> <lang>")
    sys.exit(1)

# Create the object, defining the language to use and the policy
# Further customization is possible by providing a config
proc = PiiTextProcessor(lang=sys.argv[2], default_policy="annotate", debug=True)

# Process a text buffer and get the transformed buffer
with open(sys.argv[1], "rt", encoding="utf-8") as f:
    input = f.read()
outbuf = proc(input)

print(outbuf)
