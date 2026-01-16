from src.pipeline.orchestrator import NewsOrchestrator

if __name__ == "__main__":
    orchestrator = NewsOrchestrator()
    orchestrator.run_cycle()