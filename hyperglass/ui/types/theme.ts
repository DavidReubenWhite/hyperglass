import type { ColorHues } from '@chakra-ui/theme/dist/types/foundations/colors';

interface ChakraColors {
  transparent: string;
  current: string;
  black: string;
  white: string;
  whiteAlpha: ColorHues;
  blackAlpha: ColorHues;
  gray: ColorHues;
  red: ColorHues;
  orange: ColorHues;
  yellow: ColorHues;
  green: ColorHues;
  teal: ColorHues;
  blue: ColorHues;
  cyan: ColorHues;
  purple: ColorHues;
  pink: ColorHues;
  linkedin: ColorHues;
  facebook: ColorHues;
  messenger: ColorHues;
  whatsapp: ColorHues;
  twitter: ColorHues;
  telegram: ColorHues;
}

interface CustomColors {
  primary: ColorHues;
  secondary: ColorHues;
  tertiary: ColorHues;
  dark: ColorHues;
  light: ColorHues;
}

type AllColors = CustomColors & ChakraColors;
type ColorKey = keyof AllColors;

export interface Colors extends AllColors {
  original: { [key in ColorKey]: string };
}

export interface Fonts {
  body: string;
  mono: string;
}