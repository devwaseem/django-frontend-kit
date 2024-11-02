import "@shared/main";
import "./index.css";

import Alpine, { AlpineComponent } from "alpinejs";

interface HomeComponent extends AlpineComponent {
  showAlert(): void;
}

Alpine.data(
  "home",
  (): HomeComponent => ({
    revealed: false,
    showAlert() {
      alert("Hello World");
    },
  }),
);
