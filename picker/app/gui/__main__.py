import argparse

from picker.app.gui.main import MyApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Dota 2 Hero Picker GUI")
    parser.add_argument("--model", default="latest", help="Path to the model file (default: latest)")
    args = parser.parse_args()

    root = MyApp(model_path=args.model)
    root.mainloop()


if __name__ == "__main__":
    main()
