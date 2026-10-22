from document_parser_skill import run_document_parser
from file_gen_tools_skill import run_file_gen_tools
from grammar_auditor_skill import run_grammar_auditor

print("1. Testing File Gen Tools...")
res1 = run_file_gen_tools(
    "Create a very short 2-sentence cover letter for a Software Engineer role. Keep it brief."
)
print("Result:", res1)

print("\n2. Testing Grammar Auditor...")
res2 = run_grammar_auditor(
    "Me am very good at programming. I writes code good and fast."
)
print("Result:", res2)

print("\n3. Testing Document Parser...")
# We'll create a dummy text file to parse instead of docx/pdf to keep the test simple
with open("test_dummy.txt", "w", encoding="utf-8") as f:
    f.write("This is a test document for the parser.")
res3 = run_document_parser("test_dummy.txt")
print("Result:", res3)
