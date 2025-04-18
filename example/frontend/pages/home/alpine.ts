import Alpine from "alpinejs";

interface HomeComponent {
    index: number;
    increment(): void;
}

Alpine.data(
    "HomeComponent",
    (): HomeComponent => ({
        index: 0,
        increment() {
            this.index++;
        }
    }),
);