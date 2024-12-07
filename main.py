import os
import shutil
import hashlib
import argparse
import time
import logging

def calculate_md5(file_path):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def synchronize_folders(source, replica, logger):
    """
    Synchronize the content of the source folder to the replica folder.
    """
    # Ensure the replica folder exists
    if not os.path.exists(replica):
        os.makedirs(replica)
        logger.info(f"Created directory: {replica}")

    # Get lists of files and directories
    source_items = set(os.listdir(source))
    replica_items = set(os.listdir(replica))

    # Handle files and directories in source
    for item in source_items:
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)

        if os.path.isdir(source_item_path):
            # Recursively synchronize directories
            synchronize_folders(source_item_path, replica_item_path, logger)
        else:
            # Synchronize files
            if not os.path.exists(replica_item_path) or \
               calculate_md5(source_item_path) != calculate_md5(replica_item_path):
                shutil.copy2(source_item_path, replica_item_path)
                logger.info(f"Copied/Updated file: {source_item_path} -> {replica_item_path}")

    # Handle items in replica that are not in source
    for item in replica_items - source_items:
        replica_item_path = os.path.join(replica, item)
        if os.path.isdir(replica_item_path):
            shutil.rmtree(replica_item_path)
            logger.info(f"Removed directory: {replica_item_path}")
        else:
            os.remove(replica_item_path)
            logger.info(f"Removed file: {replica_item_path}")

def main():
    parser = argparse.ArgumentParser(description="Folder Synchronizer")
    parser.add_argument("--source", required=True, help="Path to the source folder")
    parser.add_argument("--replica", required=True, help="Path to the replica folder")
    parser.add_argument("--interval", type=int, required=True, help="Synchronization interval in seconds")
    parser.add_argument("--log_file", required=True, help="Path to the log file")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        filename=args.log_file,
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
    )
    logger = logging.getLogger()

    # Run periodic synchronization
    try:
        while True:
            logger.info("Starting synchronization...")
            synchronize_folders(args.source, args.replica, logger)
            logger.info("Synchronization complete. Sleeping...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Program terminated by user.")
        print("\nProgram terminated.")

if __name__ == "__main__":
    main()
