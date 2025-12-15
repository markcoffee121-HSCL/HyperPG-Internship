# Day 14 - Baseline Performance Results

## Test Configuration

- File Processor: http://localhost:9030
- Summarizer: http://localhost:9040
- Web UI: http://localhost:5000

## Results Summary

| Test Type         | Target         | Response Time   | Status   |
|-------------------|----------------|-----------------|----------|
| Health Check      | File Processor | 2062.46ms       | Success  |
| Health Check      | Summarizer     | 2007.01ms       | Success  |
| Health Check      | Web UI         | 6019.96ms       | Success  |
| File Processor    | small_1kb.txt  | 2010.52ms       | Success  |
| File Processor    | medium_5kb.txt | 2023.84ms       | Success  |
| File Processor    | large_10kb.txt | 2022.75ms       | Success  |
| Summarizer        | small_1kb.txt  | 2583.33ms       | Success  |
| Summarizer        | medium_5kb.txt | 2416.07ms       | Success  |
| Repeated Requests | Average        | 2019.93ms       | Success  |
| Repeated Requests | Min            | 2012.09ms       | Success  |
| Repeated Requests | Max            | 2028.78ms       | Success  |

## Notes

- All times measured in milliseconds (ms)
- Tests run without caching
- Groq LLM calls add significant latency
- Repeated requests show no caching benefit (yet)
