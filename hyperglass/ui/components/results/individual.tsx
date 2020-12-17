import { forwardRef, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Flex,
  Alert,
  Tooltip,
  ButtonGroup,
  AccordionItem,
  AccordionPanel,
  AccordionButton,
} from '@chakra-ui/react';
import { BsLightningFill } from '@meronex/icons/bs';
import { startCase } from 'lodash';
import { BGPTable, Countdown, CopyButton, RequeryButton, TextOutput, If } from '~/components';
import { useColorValue, useConfig, useMobile } from '~/context';
import { useStrf, useLGQuery, useTableToString } from '~/hooks';
import { isStructuredOutput, isStringOutput } from '~/types';
import { FormattedError } from './error';
import { ResultHeader } from './header';
import { isStackError, isFetchError, isLGError } from './guards';

import type { TAccordionHeaderWrapper, TResult, TErrorLevels } from './types';

const AccordionHeaderWrapper = (props: TAccordionHeaderWrapper) => {
  const { hoverBg, ...rest } = props;
  return (
    <Flex
      justify="space-between"
      _hover={{ bg: hoverBg }}
      _focus={{ boxShadow: 'outline' }}
      {...rest}
    />
  );
};

export const Result = forwardRef<HTMLDivElement, TResult>((props, ref) => {
  const {
    index,
    device,
    queryVrf,
    queryType,
    queryTarget,
    setComplete,
    queryLocation,
    resultsComplete,
  } = props;

  const { web, cache, messages } = useConfig();
  const isMobile = useMobile();
  const color = useColorValue('black', 'white');
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');

  const { data, error, isError, isLoading, refetch } = useLGQuery({
    queryLocation,
    queryTarget,
    queryType,
    queryVrf,
  });

  const cacheLabel = useStrf(web.text.cache_icon, { time: data?.timestamp }, [data?.timestamp]);

  const [isOpen, setOpen] = useState(false);
  const [hasOverride, setOverride] = useState(false);

  const handleToggle = () => {
    setOpen(!isOpen);
    setOverride(true);
  };

  const errorKeywords = useMemo(() => {
    let kw = [] as string[];
    if (isLGError(error)) {
      kw = error.keywords;
    }
    return kw;
  }, [isError]);

  let errorMsg;

  if (isLGError(error)) {
    errorMsg = error.output as string;
  } else if (isFetchError(error)) {
    errorMsg = startCase(error.statusText);
  } else if (isStackError(error) && error.message.toLowerCase().startsWith('timeout')) {
    errorMsg = messages.request_timeout;
  } else if (isStackError(error)) {
    errorMsg = startCase(error.message);
  } else {
    errorMsg = messages.general;
  }

  error && console.error(error);

  const errorLevel = useMemo<TErrorLevels>(() => {
    const statusMap = {
      success: 'success',
      warning: 'warning',
      error: 'warning',
      danger: 'error',
    } as { [k in TResponseLevel]: 'success' | 'warning' | 'error' };

    let e: TErrorLevels = 'error';

    if (isLGError(error)) {
      const idx = error.level as TResponseLevel;
      e = statusMap[idx];
    }
    return e;
  }, [error]);

  const tableComponent = useMemo<boolean>(() => {
    let result = false;
    if (typeof queryType.match(/^bgp_\w+$/) !== null && data?.format === 'application/json') {
      result = true;
    }
    return result;
  }, [queryType, data?.format]);

  let copyValue = data?.output as string;

  const formatData = useTableToString(queryTarget, data, [data?.format]);

  if (data?.format === 'application/json') {
    copyValue = formatData();
  }

  if (error) {
    copyValue = errorMsg;
  }

  useEffect(() => {
    if (isLoading && resultsComplete === null) {
      setComplete(index);
    }
  }, [isLoading, resultsComplete]);

  useEffect(() => {
    if (resultsComplete === index && !hasOverride) {
      setOpen(true);
    }
  }, [resultsComplete, index]);

  return (
    <AccordionItem
      ref={ref}
      isDisabled={isLoading}
      css={{
        '&:last-of-type': { borderBottom: 'none' },
        '&:first-of-type': { borderTop: 'none' },
      }}>
      <AccordionHeaderWrapper hoverBg="blackAlpha.50">
        <AccordionButton
          py={2}
          w="unset"
          _hover={{}}
          _focus={{}}
          flex="1 0 auto"
          onClick={handleToggle}>
          <ResultHeader
            isError={isError}
            loading={isLoading}
            errorMsg={errorMsg}
            errorLevel={errorLevel}
            runtime={data?.runtime ?? 0}
            title={device.display_name}
          />
        </AccordionButton>
        <ButtonGroup px={[1, 1, 3, 3]} py={2}>
          <CopyButton copyValue={copyValue} isDisabled={isLoading} />
          <RequeryButton requery={refetch} isDisabled={isLoading} />
        </ButtonGroup>
      </AccordionHeaderWrapper>
      <AccordionPanel
        pb={4}
        overflowX="auto"
        css={{
          WebkitOverflowScrolling: 'touch',
          '&::-webkit-scrollbar': { height: '5px' },
          '&::-webkit-scrollbar-track': {
            backgroundColor: scrollbarBg,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: scrollbar,
          },
          '&::-webkit-scrollbar-thumb:hover': {
            backgroundColor: scrollbarHover,
          },

          '-ms-overflow-style': { display: 'none' },
        }}>
        <Box>
          <Flex direction="column" flex="1 0 auto" maxW={error ? '100%' : undefined}>
            {!isError && typeof data !== 'undefined' && (
              <>
                {isStructuredOutput(data) && data.level === 'success' && tableComponent ? (
                  <BGPTable>{data.output}</BGPTable>
                ) : isStringOutput(data) && data.level === 'success' && !tableComponent ? (
                  <TextOutput>{data.output}</TextOutput>
                ) : isStringOutput(data) && data.level !== 'success' ? (
                  <Alert rounded="lg" my={2} py={4} status={errorLevel}>
                    <FormattedError message={data.output} keywords={errorKeywords} />
                  </Alert>
                ) : null}
              </>
            )}
          </Flex>
        </Box>

        <Flex direction="row" flexWrap="wrap">
          <Flex
            px={3}
            mt={2}
            justifyContent={['flex-start', 'flex-start', 'flex-end', 'flex-end']}
            flex="1 0 auto">
            <If c={cache.show_text && typeof data !== 'undefined' && !error}>
              <If c={!isMobile}>
                <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
              </If>
              <Tooltip
                display={!data?.cached ? 'none' : undefined}
                hasArrow
                label={cacheLabel}
                placement="top">
                <Box ml={1} display={data?.cached ? 'block' : 'none'}>
                  <BsLightningFill color={color} />
                </Box>
              </Tooltip>
              <If c={isMobile}>
                <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
              </If>
            </If>
          </Flex>
        </Flex>
      </AccordionPanel>
    </AccordionItem>
  );
});