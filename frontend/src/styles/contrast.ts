// Contrast helper (WCAG approximate calculation)
// Formula based on relative luminance

function hexToRgb(hex: string) {
  const h = hex.replace('#','');
  const bigint = parseInt(h.length === 3 ? h.split('').map(c=>c+c).join('') : h, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255
  };
}

function relativeLuminance({r,g,b}:{r:number;g:number;b:number}) {
  const toLin = (c:number) => {
    const v = c/255;
    return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4);
  };
  const R = toLin(r), G = toLin(g), B = toLin(b);
  return 0.2126*R + 0.7152*G + 0.0722*B;
}

export function contrastRatio(fgHex: string, bgHex: string): number {
  const L1 = relativeLuminance(hexToRgb(fgHex));
  const L2 = relativeLuminance(hexToRgb(bgHex));
  const lighter = Math.max(L1, L2);
  const darker = Math.min(L1, L2);
  return Number(((lighter + 0.05) / (darker + 0.05)).toFixed(2));
}

export function meetsAA(textHex: string, bgHex: string, large: boolean = false): boolean {
  const ratio = contrastRatio(textHex, bgHex);
  return ratio >= (large ? 3.0 : 4.5);
}

export function assertContrast(name: string, textHex: string, bgHex: string, large = false) {
  if (!meetsAA(textHex, bgHex, large)) {
    // eslint-disable-next-line no-console
    console.warn(`Contrast check failed for ${name} (${textHex} on ${bgHex}) ratio=${contrastRatio(textHex,bgHex)}`);
  }
}
