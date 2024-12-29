// config/languages.ts
import { LanguageSupport } from "@codemirror/language";
import { javascript } from "@codemirror/lang-javascript";
import { python } from "@codemirror/lang-python";
import { java } from "@codemirror/lang-java";
import { rust } from "@codemirror/lang-rust";
import { cpp } from "@codemirror/lang-cpp";
import { go } from "@codemirror/lang-go";
import { Extension } from "@codemirror/state";

export interface LanguageConfig {
  name: string;
  extension: () => LanguageSupport;
  mime: string;
  sampleCode: string;
  // File extensions associated with this language
  fileExtensions: string[];
  // Language-specific editor configurations
  editorConfig?: {
    tabSize?: number;
    insertSpaces?: boolean;
    autoCloseBrackets?: boolean;
  };
  additionalExtensions?: Extension[];
}

export const languageConfigurations: Record<string, LanguageConfig> = {
  javascript: {
    name: "JavaScript",
    extension: () => javascript({ typescript: false }),
    mime: "application/javascript",
    fileExtensions: ["js", "mjs", "cjs"],
    sampleCode: `// JavaScript Example
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// Example usage
console.log(fibonacci(10));`,
    editorConfig: {
      tabSize: 2,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  typescript: {
    name: "TypeScript",
    extension: () => javascript({ typescript: true }),
    mime: "application/typescript",
    fileExtensions: ["ts", "tsx"],
    sampleCode: `// TypeScript Example
interface User {
  name: string;
  age: number;
}

function greet(user: User): string {
  return \`Hello, \${user.name}! You are \${user.age} years old.\`;
}

const user: User = {
  name: "John",
  age: 30
};

console.log(greet(user));`,
    editorConfig: {
      tabSize: 2,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  python: {
    name: "Python",
    extension: () => python(),
    mime: "text/x-python",
    fileExtensions: ["py", "pyw"],
    sampleCode: `# Python Example
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# Example usage
numbers = [3, 6, 8, 10, 1, 2, 1]
print(quick_sort(numbers))`,
    editorConfig: {
      tabSize: 4,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  java: {
    name: "Java",
    extension: () => java(),
    mime: "text/x-java",
    fileExtensions: ["java"],
    sampleCode: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
        
        // Example of a simple class
        Person person = new Person("Alice", 25);
        person.greet();
    }
}

class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void greet() {
        System.out.println("Hello, my name is " + name);
    }
}`,
    editorConfig: {
      tabSize: 4,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  rust: {
    name: "Rust",
    extension: () => rust(),
    mime: "text/x-rust",
    fileExtensions: ["rs"],
    sampleCode: `// Rust Example
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

fn main() {
    let rect = Rectangle {
        width: 30,
        height: 50,
    };

    println!(
        "The area of the rectangle is {} square pixels.",
        rect.area()
    );
}`,
    editorConfig: {
      tabSize: 4,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  go: {
    name: "Go",
    extension: () => go(),
    mime: "text/x-go",
    fileExtensions: ["go"],
    sampleCode: `package main

import "fmt"

// Simple struct example
type Person struct {
    Name string
    Age  int
}

func (p Person) SayHello() {
    fmt.Printf("Hello, my name is %s and I'm %d years old\n", p.Name, p.Age)
}

func main() {
    person := Person{Name: "Alice", Age: 25}
    person.SayHello()
}`,
    editorConfig: {
      tabSize: 4,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },

  cpp: {
    name: "C++",
    extension: () => cpp(),
    mime: "text/x-c++src",
    fileExtensions: ["cpp", "cc", "h", "hpp"],
    sampleCode: `#include <iostream>
#include <vector>

class Shape {
public:
    virtual double area() = 0;
    virtual ~Shape() {}
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(double r) : radius(r) {}
    
    double area() override {
        return 3.14159 * radius * radius;
    }
};

int main() {
    Circle circle(5);
    std::cout << "Circle area: " << circle.area() << std::endl;
    return 0;
}`,
    editorConfig: {
      tabSize: 2,
      insertSpaces: true,
      autoCloseBrackets: true,
    },
  },
};

// Helper functions
export function getLanguageConfig(languageId: string): LanguageConfig {
  return (
    languageConfigurations[languageId] || languageConfigurations.javascript
  );
}

export function getLanguageByFileExtension(filename: string): string {
  const extension = filename.split(".").pop()?.toLowerCase();

  for (const [langId, config] of Object.entries(languageConfigurations)) {
    if (config.fileExtensions.includes(extension!)) {
      return langId;
    }
  }

  return "javascript"; // Default fallback
}

export function isValidLanguage(languageId: string): boolean {
  return languageId in languageConfigurations;
}

export function getLanguageByExtension(extension: string): string {
  return Object.keys(languageConfigurations).find((lang) =>
    languageConfigurations[lang].fileExtensions.includes(extension)
  )!;
}
