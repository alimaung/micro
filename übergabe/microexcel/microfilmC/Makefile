# Makefile for the microfilm processing system

# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pedantic -g -O2
LDFLAGS = -lsqlite3 -lm

# Directories
SRCDIR = .
OBJDIR = obj
BINDIR = bin

# Target executable
TARGET = $(BINDIR)/microfilm

# Source files
SOURCES = main.c models.c project_service.c document_service.c film_service.c database.c export_service.c
OBJECTS = $(SOURCES:%.c=$(OBJDIR)/%.o)

# Header files
HEADERS = microfilm.h

# Default target
all: $(TARGET)

# Create directories if they don't exist
$(OBJDIR):
	mkdir -p $(OBJDIR)

$(BINDIR):
	mkdir -p $(BINDIR)

# Build the main executable
$(TARGET): $(OBJECTS) | $(BINDIR)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

# Compile source files to object files
$(OBJDIR)/%.o: $(SRCDIR)/%.c $(HEADERS) | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -rf $(OBJDIR) $(BINDIR)

# Clean and rebuild
rebuild: clean all

# Install target (copy to /usr/local/bin)
install: $(TARGET)
	sudo cp $(TARGET) /usr/local/bin/microfilm
	sudo chmod +x /usr/local/bin/microfilm

# Uninstall target
uninstall:
	sudo rm -f /usr/local/bin/microfilm

# Debug build
debug: CFLAGS += -DDEBUG -g3 -O0
debug: $(TARGET)

# Release build
release: CFLAGS += -DNDEBUG -O3
release: clean $(TARGET)

# Run static analysis
check:
	cppcheck --enable=all --std=c99 $(SOURCES)

# Format code
format:
	clang-format -i $(SOURCES) $(HEADERS)

# Show help
help:
	@echo "Available targets:"
	@echo "  all      - Build the application (default)"
	@echo "  clean    - Remove build artifacts"
	@echo "  rebuild  - Clean and rebuild"
	@echo "  debug    - Build with debug symbols"
	@echo "  release  - Build optimized release version"
	@echo "  install  - Install to /usr/local/bin"
	@echo "  uninstall- Remove from /usr/local/bin"
	@echo "  check    - Run static analysis"
	@echo "  format   - Format source code"
	@echo "  help     - Show this help"

# Dependencies
$(OBJDIR)/main.o: main.c microfilm.h
$(OBJDIR)/models.o: models.c microfilm.h
$(OBJDIR)/project_service.o: project_service.c microfilm.h
$(OBJDIR)/document_service.o: document_service.c microfilm.h
$(OBJDIR)/film_service.o: film_service.c microfilm.h
$(OBJDIR)/database.o: database.c microfilm.h
$(OBJDIR)/export_service.o: export_service.c microfilm.h

# Phony targets
.PHONY: all clean rebuild install uninstall debug release check format help

# Print variables for debugging
print-%:
	@echo $* = $($*)

# Test target
test: $(TARGET)
	@echo "Running basic test..."
	@echo "Test project path:" > test_input.txt
	@echo "/tmp/test_project" >> test_input.txt
	@mkdir -p /tmp/test_project
	@echo "Test completed"

# Package target
package: release
	@echo "Creating package..."
	tar -czf microfilm-$(shell date +%Y%m%d).tar.gz $(BINDIR)/microfilm README.md
	@echo "Package created: microfilm-$(shell date +%Y%m%d).tar.gz"

