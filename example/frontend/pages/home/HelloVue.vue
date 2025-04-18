<script setup>
import { ref } from 'vue';
const count = ref(0);

function increment() {
    count.value++;
}
</script>

<template>
    <div class="p-6 bg-gray-50 border border-gray-200 rounded-lg flex flex-col gap-4">
        <div>This is rendered using Vue JS</div>
        <div>
            Current value: {{ count }}
        </div>
        <button type="button" @click="increment()"
            class="px-2 py-1 bg-black rounded-lg text-white cursor-pointer">Increment</button>
    </div>
</template>
