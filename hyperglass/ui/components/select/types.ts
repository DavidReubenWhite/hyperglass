import type {
  Props as IReactSelect,
  ControlProps,
  MenuProps,
  MenuListComponentProps,
  OptionProps,
  MultiValueProps,
  IndicatorProps,
  Theme,
  PlaceholderProps,
} from 'react-select';
import type { BoxProps } from '@chakra-ui/react';
import type { ColorNames, TSelectOption, TSelectOptionMulti, TSelectOptionGroup } from '~/types';

export interface TSelectState {
  [k: string]: string[];
}

export type TOptions = Array<TSelectOptionGroup | TSelectOption>;

export type TBoxAsReactSelect = Omit<IReactSelect, 'isMulti' | 'onSelect' | 'onChange'> &
  Omit<BoxProps, 'onChange' | 'onSelect'>;

export interface TSelectBase extends TBoxAsReactSelect {
  name: string;
  multi?: boolean;
  options: TOptions;
  required?: boolean;
  onSelect?: (s: TSelectOption[]) => void;
  onChange?: (c: TSelectOption | TSelectOptionMulti) => void;
  colorScheme?: ColorNames;
}

export interface TSelectContext {
  colorMode: 'light' | 'dark';
  isOpen: boolean;
}

export interface TMultiValueRemoveProps {
  children: Node;
  data: any;
  innerProps: {
    className: string;
    onTouchEnd: (e: any) => void;
    onClick: (e: any) => void;
    onMouseDown: (e: any) => void;
  };
  selectProps: any;
}

export interface TRSTheme extends Omit<Theme, 'borderRadius'> {
  borderRadius: string | number;
}

export type TControl = ControlProps<TOptions, false>;

export type TMenu = MenuProps<TOptions, false>;

export type TMenuList = MenuListComponentProps<TOptions, false>;

export type TOption = OptionProps<TOptions, false>;

export type TMultiValueState = MultiValueProps<TOptions>;

export type TIndicator = IndicatorProps<TOptions, false>;

export type TPlaceholder = PlaceholderProps<TOptions, false>;

export type TMultiValue = Pick<TSelectContext, 'colorMode'>;

export type { Styles as TStyles } from 'react-select';