"""
Generate Hashed Password Script
Generate bcrypt hashed passwords using the same method as the app.

Usage:
    python scripts/generate_hash.py
    or
    python scripts/generate_hash.py --password "your_password"
    
Note: If bcrypt is having issues, you can manually hash with:
    python -c "from passlib.context import CryptContext; c=CryptContext(schemes=['bcrypt']); print(c.hash('YourPassword123'))"
"""
import os
import sys
import argparse
import getpass

# Add Backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.core.security import get_password_hash
except Exception as e:
    print(f"Warning: Could not import get_password_hash: {e}")
    print("Will use passlib directly\n")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def get_password_hash(password: str) -> str:
        """Generate a bcrypt hash of the password."""
        return pwd_context.hash(password)


def generate_hash_interactive():
    """Generate password hash interactively."""
    print("\n" + "="*70)
    print("GENERATE BCRYPT PASSWORD HASH")
    print("="*70 + "\n")
    
    while True:
        password = getpass.getpass("Enter password (min 8, max 72 characters): ")
        
        if not password:
            print("❌ Password cannot be empty")
            continue
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        
        if len(password) > 72:
            print("❌ Password must be at most 72 characters (bcrypt limit)")
            continue
        
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords don't match")
            continue
        
        break
    
    try:
        hashed = get_password_hash(password)
        
        print("\n" + "="*70)
        print("✅ PASSWORD HASHED SUCCESSFULLY")
        print("="*70)
        print(f"\nPassword: {'*' * len(password)}")
        print(f"Hash:\n{hashed}")
        print("\n" + "="*70)
        print("Use this hash in SQL INSERT statements or database operations")
        print("="*70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error generating hash: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_hash_cli(password: str) -> bool:
    """Generate password hash from CLI argument."""
    
    # Validate password
    if not password:
        print("❌ Password cannot be empty")
        return False
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return False
    
    if len(password) > 72:
        print("❌ Password must be at most 72 characters (bcrypt limit)")
        return False
    
    try:
        hashed = get_password_hash(password)
        
        print("\n" + "="*70)
        print("✅ PASSWORD HASHED SUCCESSFULLY")
        print("="*70)
        print(f"\nPassword: {'*' * len(password)}")
        print(f"Length: {len(password)} characters")
        print(f"\nHash:\n{hashed}")
        print("\n" + "="*70)
        print("Use this hash in SQL INSERT statements or database operations")
        print("="*70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error generating hash: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate bcrypt password hash",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/generate_hash.py
  
  # CLI mode
  python scripts/generate_hash.py --password "MySecurePassword123!"
  
  # With password from stdin
  echo "MyPassword123!" | python scripts/generate_hash.py --stdin
        """
    )
    
    parser.add_argument(
        "--password",
        default=None,
        help="Password to hash (if not provided, will prompt interactively)"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read password from stdin instead of arguments"
    )
    
    args = parser.parse_args()
    
    # Determine which mode to use
    if args.stdin:
        password = sys.stdin.readline().strip()
        if not password:
            print("❌ No password provided on stdin")
            return False
        return generate_hash_cli(password)
    elif args.password:
        return generate_hash_cli(args.password)
    else:
        return generate_hash_interactive()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
