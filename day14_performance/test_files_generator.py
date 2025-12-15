"""
Generate test files of various sizes for benchmarking
"""
import os

def generate_test_files():
    """Generate test files of different sizes"""
    
    # Create test_files directory
    os.makedirs("test_files", exist_ok=True)
    
    # Small file (1KB - ~150 words)
    small_content = "This is a test file for benchmarking. " * 25
    with open("test_files/small_1kb.txt", "w", encoding="utf-8") as f:
        f.write(small_content)
    
    # Medium file (5KB - ~750 words)
    medium_content = "This is a medium sized test file for performance testing. " * 90
    with open("test_files/medium_5kb.txt", "w", encoding="utf-8") as f:
        f.write(medium_content)
    
    # Large file (10KB - ~1500 words)
    large_content = "This is a larger test file to measure performance with bigger inputs. " * 150
    with open("test_files/large_10kb.txt", "w", encoding="utf-8") as f:
        f.write(large_content)
    
    # Very large file (50KB - ~7500 words, will exceed Groq limits)
    very_large_content = "This is a very large test file that will exceed token limits. " * 800
    with open("test_files/very_large_50kb.txt", "w", encoding="utf-8") as f:
        f.write(very_large_content)
    
    print("Test files generated:")
    for filename in ["small_1kb.txt", "medium_5kb.txt", "large_10kb.txt", "very_large_50kb.txt"]:
        filepath = f"test_files/{filename}"
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size} bytes ({size/1024:.2f} KB)")

if __name__ == "__main__":
    generate_test_files()