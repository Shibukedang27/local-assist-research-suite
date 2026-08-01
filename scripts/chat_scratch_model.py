"""Interactive chat using only the local from-scratch checkpoint and exact gates."""

from local_assist.scratch_assistant import answer, load_default

if __name__ == "__main__":
    model = load_default()
    print("Local Assist Tiny — trained from scratch on this Mac. Type /quit to exit.")
    while True:
        try:
            prompt = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if prompt.lower() in {"/quit", "/exit"}:
            break
        if prompt:
            result = answer(model, prompt)
            print(f"AI [{result['route']}]> {result['answer']}\n")
