import { useEffect, useCallback, useRef } from 'react'

interface UseScannerOptions {
  onScan: (value: string) => void
  minLength?: number
  maxDelay?: number
}

/**
 * Hook to handle barcode scanner input.
 * Barcode scanners typically act as keyboards - they type the barcode and press Enter.
 * This hook detects rapid input followed by Enter key.
 */
export function useScanner({ onScan, minLength = 3, maxDelay = 50 }: UseScannerOptions) {
  const bufferRef = useRef<string>('')
  const lastKeyTimeRef = useRef<number>(0)

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const now = Date.now()
      
      // If it's been too long since the last key, reset the buffer
      if (now - lastKeyTimeRef.current > maxDelay) {
        bufferRef.current = ''
      }
      lastKeyTimeRef.current = now

      if (event.key === 'Enter') {
        if (bufferRef.current.length >= minLength) {
          onScan(bufferRef.current)
        }
        bufferRef.current = ''
      } else if (event.key.length === 1) {
        // Only add printable characters
        bufferRef.current += event.key
      }
    },
    [onScan, minLength, maxDelay]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  const clearBuffer = useCallback(() => {
    bufferRef.current = ''
  }, [])

  return { clearBuffer }
}
