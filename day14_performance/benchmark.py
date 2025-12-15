"""
Performance benchmarking tool for HyperPG AIMs
Measures response times, latency, and throughput
"""
import requests
import time
import json
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
FILE_PROCESSOR_URL = "http://localhost:9030"
SUMMARIZER_URL = "http://localhost:9040"
WEB_UI_URL = "http://localhost:5000"

class Benchmark:
    def __init__(self):
        self.results = []
    
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, (end - start) * 1000  # Return result and time in ms
    
    def test_health_checks(self):
        """Test health check response times"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"TEST 1: Health Check Response Times")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        tests = [
            ("File Processor", f"{FILE_PROCESSOR_URL}/health"),
            ("Summarizer", f"{SUMMARIZER_URL}/health"),
            ("Web UI", f"{WEB_UI_URL}/health")
        ]
        
        for name, url in tests:
            try:
                _, elapsed = self.measure_time(requests.get, url, timeout=5)
                status = f"{Fore.GREEN}✓ Online{Style.RESET_ALL}"
                print(f"{name:20} {status:20} {elapsed:8.2f}ms")
                self.results.append(["Health Check", name, f"{elapsed:.2f}ms", "Success"])
            except Exception as e:
                status = f"{Fore.RED}✗ Offline{Style.RESET_ALL}"
                print(f"{name:20} {status:20} Error")
                self.results.append(["Health Check", name, "N/A", f"Failed: {str(e)[:30]}"])
    
    def test_file_processor(self, filename, filepath):
        """Test File Processor AIM with a specific file"""
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                response, elapsed = self.measure_time(
                    requests.post,
                    f"{FILE_PROCESSOR_URL}/process",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                return elapsed, "Success", data
            else:
                return elapsed, f"Error {response.status_code}", None
        except Exception as e:
            return 0, f"Failed: {str(e)[:30]}", None
    
    def test_summarizer(self, text):
        """Test Summarizer AIM with text"""
        try:
            payload = {"text": text}
            response, elapsed = self.measure_time(
                requests.post,
                f"{SUMMARIZER_URL}/summarize",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return elapsed, "Success", data
            else:
                return elapsed, f"Error {response.status_code}", None
        except Exception as e:
            return 0, f"Failed: {str(e)[:30]}", None
    
    def test_file_processing(self):
        """Test file processing with different file sizes"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"TEST 2: File Processor Performance")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        test_files = [
            ("small_1kb.txt", "test_files/small_1kb.txt"),
            ("medium_5kb.txt", "test_files/medium_5kb.txt"),
            ("large_10kb.txt", "test_files/large_10kb.txt"),
        ]
        
        for filename, filepath in test_files:
            elapsed, status, data = self.test_file_processor(filename, filepath)
            
            if data:
                print(f"{filename:20} {Fore.GREEN}{status:15}{Style.RESET_ALL} {elapsed:8.2f}ms")
                self.results.append(["File Processor", filename, f"{elapsed:.2f}ms", status])
            else:
                print(f"{filename:20} {Fore.RED}{status:15}{Style.RESET_ALL}")
                self.results.append(["File Processor", filename, "N/A", status])
    
    def test_summarization(self):
        """Test summarization with different text sizes"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"TEST 3: Summarizer Performance (with Groq LLM)")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        test_files = [
            ("small_1kb.txt", "test_files/small_1kb.txt"),
            ("medium_5kb.txt", "test_files/medium_5kb.txt"),
        ]
        
        for filename, filepath in test_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            elapsed, status, data = self.test_summarizer(text)
            
            if "Success" in status:
                print(f"{filename:20} {Fore.GREEN}{status:15}{Style.RESET_ALL} {elapsed:8.2f}ms")
                self.results.append(["Summarizer", filename, f"{elapsed:.2f}ms", status])
            else:
                print(f"{filename:20} {Fore.YELLOW}{status:15}{Style.RESET_ALL}")
                self.results.append(["Summarizer", filename, "N/A", status])
    
    def test_repeated_requests(self):
        """Test repeated requests to measure consistency"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"TEST 4: Repeated Request Performance (No Caching)")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        filename = "small_1kb.txt"
        filepath = "test_files/small_1kb.txt"
        iterations = 5
        
        times = []
        for i in range(iterations):
            elapsed, status, _ = self.test_file_processor(filename, filepath)
            if "Success" in status:
                times.append(elapsed)
                print(f"  Request {i+1}: {elapsed:8.2f}ms")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{Fore.YELLOW}Statistics:{Style.RESET_ALL}")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Min:     {min_time:.2f}ms")
            print(f"  Max:     {max_time:.2f}ms")
            
            self.results.append(["Repeated Requests", "Average", f"{avg_time:.2f}ms", "Success"])
            self.results.append(["Repeated Requests", "Min", f"{min_time:.2f}ms", "Success"])
            self.results.append(["Repeated Requests", "Max", f"{max_time:.2f}ms", "Success"])
    
    def save_results(self):
        """Save results to markdown file"""
        with open("baseline_results.md", "w", encoding="utf-8") as f:
            f.write("# Day 14 - Baseline Performance Results\n\n")
            f.write("## Test Configuration\n\n")
            f.write(f"- File Processor: {FILE_PROCESSOR_URL}\n")
            f.write(f"- Summarizer: {SUMMARIZER_URL}\n")
            f.write(f"- Web UI: {WEB_UI_URL}\n\n")
            
            f.write("## Results Summary\n\n")
            headers = ["Test Type", "Target", "Response Time", "Status"]
            f.write(tabulate(self.results, headers=headers, tablefmt="github"))
            f.write("\n\n")
            
            f.write("## Notes\n\n")
            f.write("- All times measured in milliseconds (ms)\n")
            f.write("- Tests run without caching\n")
            f.write("- Groq LLM calls add significant latency\n")
            f.write("- Repeated requests show no caching benefit (yet)\n")
        
        print(f"\n{Fore.GREEN}Results saved to: baseline_results.md{Style.RESET_ALL}")
    
    def run_all(self):
        """Run all benchmark tests"""
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"HyperPG AIMs Performance Benchmark")
        print(f"Day 14 - Baseline Measurements")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        self.test_health_checks()
        self.test_file_processing()
        self.test_summarization()
        self.test_repeated_requests()
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"Benchmark Complete")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        self.save_results()

if __name__ == "__main__":
    # Generate test files first
    print("Generating test files...")
    from test_files_generator import generate_test_files
    generate_test_files()
    
    # Run benchmarks
    benchmark = Benchmark()
    benchmark.run_all()