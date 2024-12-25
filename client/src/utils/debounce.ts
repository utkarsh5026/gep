/**
 * Debounce a function
 * @param func - The function to debounce
 * @param delay - The delay in milliseconds
 * @returns The debounced function
 */
function debounce<T extends (...args: unknown[]) => ReturnType<T>>(
  func: T,
  delay: number
): T & { cancel: () => void } {
  let timeoutId: NodeJS.Timeout;

  const debouncedFunction = (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };

  debouncedFunction.cancel = () => clearTimeout(timeoutId);
  return debouncedFunction as T & { cancel: () => void };
}

export default debounce;
