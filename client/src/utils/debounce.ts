/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Debounce a function, with proper async support
 * @param func - The function to debounce
 * @param delay - The delay in milliseconds
 * @returns The debounced function
 */
function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => Promise<ReturnType<T>>) & {
  cancel: () => void;
} {
  let timeoutId: NodeJS.Timeout | undefined;
  const debouncedFunction = (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    return new Promise<ReturnType<T>>((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await func(...args);
          resolve(result);
        } catch (error) {
          reject(error instanceof Error ? error : new Error(String(error)));
        }
      }, delay);
    });
  };

  debouncedFunction.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = undefined;
    }
  };

  return debouncedFunction;
}

export default debounce;
