import pandas as pd
import numpy as np
import os
import argparse
from app.model.ml_model import DriverBehaviorModel

def main():
    """Train the driver behavior model using the provided data."""
    parser = argparse.ArgumentParser(description='Train the driver behavior model')
    parser.add_argument('--train', required=True, help='Path to training data CSV file')
    parser.add_argument('--test', help='Path to test data CSV file for evaluation')
    parser.add_argument('--output', default='app/model/trained_models/driver_model.pkl', help='Path to save the trained model')
    
    args = parser.parse_args()
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Initialize model
    model = DriverBehaviorModel(model_path=args.output)
    
    # Train model
    print(f"Training model using data from {args.train}...")
    result = model.train(args.train)
    
    if 'error' in result:
        print(f"Error training model: {result['error']}")
        return
    
    print(f"Model trained successfully with accuracy: {result['accuracy']:.4f}")
    print(f"Model saved to {args.output}")
    
    # Evaluate model if test data is provided
    if args.test:
        print(f"\nEvaluating model using data from {args.test}...")
        eval_result = model.evaluate(args.test)
        
        if 'error' in eval_result:
            print(f"Error evaluating model: {eval_result['error']}")
            return
        
        print(f"Evaluation accuracy: {eval_result['accuracy']:.4f}")
        print("\nClassification Report:")
        for class_name, metrics in eval_result['classification_report'].items():
            if isinstance(metrics, dict):
                print(f"  {class_name}:")
                print(f"    Precision: {metrics['precision']:.4f}")
                print(f"    Recall: {metrics['recall']:.4f}")
                print(f"    F1-score: {metrics['f1-score']:.4f}")
                print(f"    Support: {metrics['support']}")

if __name__ == '__main__':
    main()
