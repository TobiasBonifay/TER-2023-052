#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CHUNK_SIZE (1024 * 1024) // 1MB
#define TOTAL_MEMORY (1024 * 1024 * 1024) // 1GB
#define TOTAL_CHUNKS (TOTAL_MEMORY / CHUNK_SIZE)

// memory stress test
// run gcc -o steal_memory StealMemory.c
// run ./steal_memory on apache server
int main() {
    srand(time(NULL)); // Seed the random number generator

    // Allocate and write to memory in chunks
    for (int i = 0; i < TOTAL_CHUNKS; i++) {
        char *memory = malloc(CHUNK_SIZE);
        if (memory == NULL) {
            fprintf(stderr, "Failed to allocate memory\n");
            exit(EXIT_FAILURE);
        }

        // Write random values to the allocated memory
        for (int j = 0; j < CHUNK_SIZE; j++) {
            memory[j] = rand() % 256;
        }
    }

    printf("Allocated and initialized %dMB of memory\n", TOTAL_MEMORY / (1024 * 1024));

    // To keep the program running and prevent the OS from reclaiming the memory
    getchar();

    return EXIT_SUCCESS;
}