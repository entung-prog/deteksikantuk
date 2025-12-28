"""
Model Converter - Convert TFLite model to compatible version
This script attempts to load a Keras model and convert it to TFLite
with compatibility settings for TensorFlow 2.15/2.16 on ARM64.
"""

import tensorflow as tf
import sys
import os

def convert_model_to_compatible_tflite(keras_model_path, output_path):
    """
    Convert a Keras model to TFLite with compatibility settings.
    
    Args:
        keras_model_path: Path to the .h5 or SavedModel
        output_path: Path where to save the compatible .tflite file
    """
    try:
        # Load the Keras model
        print(f"Loading Keras model from: {keras_model_path}")
        print(f"TensorFlow version: {tf.__version__}")
        print(f"Keras version: {tf.keras.__version__}")
        
        # Try loading with current Keras
        try:
            model = tf.keras.models.load_model(keras_model_path)
            print(f"✅ Model loaded successfully")
        except Exception as e:
            print(f"⚠️  Standard loading failed, trying legacy Keras mode...")
            os.environ["TF_USE_LEGACY_KERAS"] = "1"
            import importlib
            importlib.reload(tf)
            model = tf.keras.models.load_model(keras_model_path)
            print(f"✅ Model loaded with legacy Keras mode")
        
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        
        # Create converter with compatibility settings
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Set compatibility options
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS  # Use only built-in ops
        ]
        
        # Optional: Enable optimizations but maintain compatibility
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Convert the model
        print("\nConverting to TFLite with compatibility settings...")
        tflite_model = converter.convert()
        
        # Save the model
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"✅ Compatible TFLite model saved to: {output_path}")
        print(f"   Size: {len(tflite_model) / 1024 / 1024:.2f} MB")
        
        # Test loading the model
        print("\nTesting model loading...")
        interpreter = tf.lite.Interpreter(model_path=output_path)
        interpreter.allocate_tensors()
        print("✅ Model loads successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("TFLite Model Compatibility Converter")
    print("="*60)
    print()
    
    # Check if Keras model exists
    keras_paths = [
        "best_model.h5",
        "model.h5",
        "saved_model",
        "../best_model.h5",
        "../model.h5"
    ]
    
    keras_model = None
    for path in keras_paths:
        if os.path.exists(path):
            keras_model = path
            print(f"Found Keras model: {path}")
            break
    
    if keras_model is None:
        print("❌ No Keras model found!")
        print("\nPlease provide the path to your Keras model (.h5 or SavedModel directory)")
        print("Usage: python convert_model.py <path_to_keras_model> [output_path]")
        print("\nSearched in:")
        for path in keras_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    output_path = "best_model_compatible.tflite"
    if len(sys.argv) > 1:
        keras_model = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    success = convert_model_to_compatible_tflite(keras_model, output_path)
    
    if success:
        print("\n" + "="*60)
        print("✅ Conversion successful!")
        print("="*60)
        print(f"\nNext steps:")
        print(f"1. Backup your current model: mv best_model.tflite best_model.tflite.backup")
        print(f"2. Use the new model: mv {output_path} best_model.tflite")
        print(f"3. Restart your application")
    else:
        print("\n" + "="*60)
        print("❌ Conversion failed!")
        print("="*60)
        print("\nYou need the original Keras model (.h5 file) to create a compatible TFLite model.")
        print("Please locate the .h5 file from your training process.")
