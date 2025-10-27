"""
Outlook MSG Recipient Changer
Changes recipients in .msg files, specifically replacing ali.maung@* addresses
with default Rolls-Royce email recipients.

Requires: pywin32 (pip install pywin32)
"""

import win32com.client
import os
import sys

# Default recipients to use when replacing ali.maung@* addresses
DEFAULT_EMAIL_RECIPIENTS = {
    'to': 'Dilek.kursun@rolls-royce.com', 
    'cc': 'jan.becker@rolls-royce.com; thomas.lux@rolls-royce.com',
    'bcc': 'michael.wuske@rolls-royce.com; tetiana.isakii@rolls-royce.com; shmaila.aslam@rolls-royce.com'
}


def should_replace_recipient(email_address):
    """
    Check if a recipient email should be replaced.
    Returns True if the email matches ali.maung@* pattern.
    
    Args:
        email_address: Email address to check
        
    Returns:
        bool: True if should be replaced, False otherwise
    """
    if not email_address:
        return False
    
    email_lower = email_address.lower()
    return email_lower.startswith('ali.maung@')


def get_recipient_email(recipient):
    """
    Extract email address from a recipient object.
    
    Args:
        recipient: Outlook recipient object
        
    Returns:
        str: Email address
    """
    try:
        # Try to get the SMTP address
        if recipient.AddressEntry.Type == "SMTP":
            return recipient.Address
        else:
            # For Exchange addresses, try to get SMTP address
            try:
                return recipient.AddressEntry.GetExchangeUser().PrimarySmtpAddress
            except:
                return recipient.Address
    except:
        return recipient.Address


def change_msg_recipients(msg_path, output_path=None, dry_run=False):
    """
    Change recipients in a .msg file if they match ali.maung@* pattern.
    
    Args:
        msg_path: Path to the input .msg file
        output_path: Path to save the modified .msg file (if None, overwrites original)
        dry_run: If True, only print what would be changed without saving
        
    Returns:
        dict: Information about the changes made
    """
    if not os.path.exists(msg_path):
        raise FileNotFoundError(f"MSG file not found: {msg_path}")
    
    # Make path absolute
    msg_path = os.path.abspath(msg_path)
    if output_path:
        output_path = os.path.abspath(output_path)
    else:
        output_path = msg_path
    
    print(f"\nProcessing: {msg_path}")
    print("-" * 80)
    
    # Initialize Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")
    
    # Load the MSG file
    msg = outlook.CreateItemFromTemplate(msg_path)
    
    # Collect information about current recipients
    original_recipients = {
        'to': [],
        'cc': [],
        'bcc': []
    }
    
    recipients_to_remove = []
    found_ali_maung = False
    
    print("\nCurrent Recipients:")
    for i in range(1, msg.Recipients.Count + 1):
        recipient = msg.Recipients.Item(i)
        email = get_recipient_email(recipient)
        recipient_type = recipient.Type
        
        # Map type to category
        type_name = {1: 'to', 2: 'cc', 3: 'bcc'}.get(recipient_type, 'unknown')
        
        original_recipients[type_name].append(email)
        print(f"  [{type_name.upper()}] {recipient.Name} <{email}>")
        
        # Check if this recipient should be replaced
        if should_replace_recipient(email):
            recipients_to_remove.append(i)
            found_ali_maung = True
            print(f"    ⚠️  Will be removed (matches ali.maung@*)")
    
    if not found_ali_maung:
        print("\n✓ No ali.maung@* recipients found. No changes needed.")
        msg.Close(0)  # Close without saving
        return {
            'changed': False,
            'reason': 'No ali.maung@* recipients found',
            'original_recipients': original_recipients
        }
    
    if dry_run:
        print("\n🔍 DRY RUN - No changes will be saved")
        print("\nWould remove these recipients:")
        for idx in recipients_to_remove:
            recipient = msg.Recipients.Item(idx)
            email = get_recipient_email(recipient)
            print(f"  - {recipient.Name} <{email}>")
        
        print("\nWould add these recipients:")
        for recipient_type, addresses in DEFAULT_EMAIL_RECIPIENTS.items():
            if addresses:
                print(f"  [{recipient_type.upper()}] {addresses}")
        
        msg.Close(0)
        return {
            'changed': False,
            'reason': 'Dry run - no changes saved',
            'would_remove': len(recipients_to_remove),
            'original_recipients': original_recipients
        }
    
    # Remove recipients in reverse order to avoid index shifting
    print("\n✏️  Removing ali.maung@* recipients...")
    for idx in reversed(recipients_to_remove):
        recipient = msg.Recipients.Item(idx)
        email = get_recipient_email(recipient)
        print(f"  Removed: {recipient.Name} <{email}>")
        msg.Recipients.Remove(idx)
    
    # Add new recipients
    print("\n✏️  Adding new recipients...")
    
    # Add TO recipients
    if DEFAULT_EMAIL_RECIPIENTS['to']:
        for email in DEFAULT_EMAIL_RECIPIENTS['to'].split(';'):
            email = email.strip()
            if email:
                recipient = msg.Recipients.Add(email)
                recipient.Type = 1  # 1 = To
                print(f"  Added [TO]: {email}")
    
    # Add CC recipients
    if DEFAULT_EMAIL_RECIPIENTS['cc']:
        for email in DEFAULT_EMAIL_RECIPIENTS['cc'].split(';'):
            email = email.strip()
            if email:
                recipient = msg.Recipients.Add(email)
                recipient.Type = 2  # 2 = CC
                print(f"  Added [CC]: {email}")
    
    # Add BCC recipients
    if DEFAULT_EMAIL_RECIPIENTS['bcc']:
        for email in DEFAULT_EMAIL_RECIPIENTS['bcc'].split(';'):
            email = email.strip()
            if email:
                recipient = msg.Recipients.Add(email)
                recipient.Type = 3  # 3 = BCC
                print(f"  Added [BCC]: {email}")
    
    # Resolve all recipients
    print("\n🔄 Resolving recipients...")
    if not msg.Recipients.ResolveAll():
        print("  ⚠️  Warning: Not all recipients could be resolved")
    
    # Save the modified message
    print(f"\n💾 Saving to: {output_path}")
    msg.SaveAs(output_path)
    msg.Close(0)  # Close without saving again
    
    print("\n✓ Successfully updated recipients!")
    print("-" * 80)
    
    return {
        'changed': True,
        'removed_count': len(recipients_to_remove),
        'original_recipients': original_recipients,
        'output_path': output_path
    }


def find_msg_files(directory, recursive=False):
    """
    Find all .msg files in a directory.
    
    Args:
        directory: Directory path to search
        recursive: If True, search subdirectories recursively
        
    Returns:
        list: List of .msg file paths
    """
    msg_files = []
    
    if recursive:
        # Recursive search
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.msg'):
                    msg_files.append(os.path.join(root, file))
    else:
        # Non-recursive search
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and item.lower().endswith('.msg'):
                    msg_files.append(item_path)
        except (OSError, PermissionError) as e:
            print(f"Error accessing directory {directory}: {e}")
    
    return sorted(msg_files)


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Change recipients in Outlook .msg files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single MSG file (overwrites original)
  python recipient_changer.py message.msg
  
  # Process and save to a new file
  python recipient_changer.py message.msg -o modified_message.msg
  
  # Dry run to see what would change
  python recipient_changer.py message.msg --dry-run
  
  # Process all MSG files in a directory
  python recipient_changer.py -d outlook/
  
  # Process all MSG files in a directory recursively
  python recipient_changer.py -d outlook/ --recursive
  
  # Process multiple specific files
  python recipient_changer.py file1.msg file2.msg file3.msg
        """
    )
    
    parser.add_argument(
        'msg_files',
        nargs='*',
        help='Path to .msg file(s) to process'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Directory containing .msg files to process'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process .msg files in subdirectories recursively (requires -d/--directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path for the modified file (only works with single input file)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without saving'
    )
    
    args = parser.parse_args()
    
    # Collect all files to process
    files_to_process = []
    
    if args.directory:
        # Process directory
        if not os.path.isdir(args.directory):
            print(f"Error: Directory not found: {args.directory}")
            sys.exit(1)
        
        print(f"Scanning directory: {args.directory}")
        if args.recursive:
            print("  (recursive mode)")
        
        files_to_process = find_msg_files(args.directory, args.recursive)
        
        if not files_to_process:
            print(f"No .msg files found in {args.directory}")
            sys.exit(0)
        
        print(f"Found {len(files_to_process)} .msg file(s)\n")
    
    elif args.msg_files:
        # Process specified files
        files_to_process = args.msg_files
    
    else:
        # No files or directory specified
        parser.print_help()
        sys.exit(1)
    
    # Validate arguments
    if args.output and len(files_to_process) > 1:
        print("Error: --output can only be used with a single input file")
        sys.exit(1)
    
    if args.recursive and not args.directory:
        print("Error: --recursive requires --directory")
        sys.exit(1)
    
    # Process each file
    results = []
    for i, msg_file in enumerate(files_to_process, 1):
        if len(files_to_process) > 1:
            print(f"\n[{i}/{len(files_to_process)}]")
        
        try:
            result = change_msg_recipients(
                msg_file,
                output_path=args.output,
                dry_run=args.dry_run
            )
            results.append((msg_file, result, None))
        except Exception as e:
            print(f"\n❌ Error processing {msg_file}: {str(e)}")
            results.append((msg_file, None, str(e)))
    
    # Print summary
    if len(results) > 1:
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        changed = sum(1 for _, r, e in results if r and r.get('changed'))
        unchanged = sum(1 for _, r, e in results if r and not r.get('changed'))
        errors = sum(1 for _, r, e in results if e)
        
        print(f"Total files processed: {len(results)}")
        print(f"  Changed: {changed}")
        print(f"  Unchanged: {unchanged}")
        print(f"  Errors: {errors}")
        
        # List changed files
        if changed > 0:
            print("\nFiles with changes:")
            for file, result, error in results:
                if result and result.get('changed'):
                    print(f"  ✓ {file}")
        
        # List files with errors
        if errors > 0:
            print("\nFiles with errors:")
            for file, result, error in results:
                if error:
                    print(f"  ❌ {file}: {error}")


if __name__ == '__main__':
    main()

