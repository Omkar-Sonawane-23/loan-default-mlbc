export function isPositiveNumber(value: unknown): boolean {
  return typeof value === "number" && !isNaN(value) && value > 0;
}

export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}
