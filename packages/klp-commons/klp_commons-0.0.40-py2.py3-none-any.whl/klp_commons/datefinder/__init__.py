import copy
import logging
import regex as re
from dateutil import tz, parser
from klp_commons.datefinder.date_fragment import DateFragment
from .constants import (
    REPLACEMENTS,
    DELIMITERS_PATTERN,
    TIMEZONE_REPLACEMENTS,
    STRIP_CHARS,
    DATE_REGEX,
    ALL_GROUPS,
    RANGE_SPLIT_REGEX,
)

logger = logging.getLogger("datefinder")


class DateFinder(object):
    """
    Locates dates in a text
    """

    def __init__(self, base_date=None, first="month"):
        self.base_date = base_date
        self.dayfirst = False
        self.yearfirst = False
        if first == "day":
            self.dayfirst = True
        if first == "year":
            self.yearfirst = True

    def find_dates(self, text, source=True, index=True, strict=False):

        for date_string, indices, captures in self.extract_date_strings(text, strict=strict):

            #  [('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'), ('Apr', 'April'), 
            # ('May', 'May'), ('Jun', 'June'), ('Jul', 'July'), ('Aug', 'August'), 
            # ('Sep', 'Sept', 'September'), ('Oct', 'October'), ('Nov', 'November'), ('Dec', 'December')]
            date_string = date_string.replace('ago', 'aug').replace('julio', 'jul').replace('junio', 'jun').replace('enero', 'jan').replace('febrero', 'frb').replace('marzo', 'mar').replace('abril', 'apr').replace('mayo', 'may').replace('agosto', 'aug').replace('septiembre', 'sep').replace('octubre', 'oct').replace('noviembre', 'nov').replace('diciembre', 'dec').replace('enero', 'jan').replace('marz', 'mar')
            
            
            
            as_dt = self.parse_date_string(date_string, captures)
            
            if as_dt is None:
                ## Dateutil couldn't make heads or tails of it
                ## move on to next
                continue

            returnables = (as_dt,)
            if source:
                returnables = returnables + (date_string,)
            if index:
                returnables = returnables + (indices,)

            if len(returnables) == 1:
                returnables = returnables[0]
            yield returnables

    def _find_and_replace(self, date_string, captures):
        """
        :warning: when multiple tz matches exist the last sorted capture will trump
        :param date_string:
        :return: date_string, tz_string
        """
        # add timezones to replace
        cloned_replacements = copy.copy(REPLACEMENTS)  # don't mutate
        for tz_string in captures.get("timezones", []):
            cloned_replacements.update({tz_string: " "})

        date_string = date_string.lower()
        for key, replacement in cloned_replacements.items():
            # we really want to match all permutations of the key surrounded by whitespace chars except one
            # for example: consider the key = 'to'
            # 1. match 'to '
            # 2. match ' to'
            # 3. match ' to '
            # but never match r'(\s|)to(\s|)' which would make 'october' > 'ocber'
            # but also include delimiters, like this 'date: '
            full_match_pattern = (
                r"(^|{delimiters_pattern}){key}($|{delimiters_pattern})".format(
                    delimiters_pattern=DELIMITERS_PATTERN, key=key
                )
            )
            date_string = re.sub(
                full_match_pattern,
                replacement,
                date_string,
                flags=re.IGNORECASE,
            )

        return date_string, self._pop_tz_string(sorted(captures.get("timezones", [])))

    def _pop_tz_string(self, list_of_timezones):
        try:
            tz_string = list_of_timezones.pop()
            # make sure it's not a timezone we
            # want replaced with better abbreviation
            return TIMEZONE_REPLACEMENTS.get(tz_string, tz_string)
        except IndexError:
            return ""

    def _add_tzinfo(self, datetime_obj, tz_string):
        """
        take a naive datetime and add dateutil.tz.tzinfo object

        :param datetime_obj: naive datetime object
        :return: datetime object with tzinfo
        """
        if datetime_obj is None:
            return None

        tzinfo_match = tz.gettz(tz_string)
        return datetime_obj.replace(tzinfo=tzinfo_match)

    def parse_date_string(self, date_string, captures):
        # For well formatted string, we can already let dateutils parse them
        # otherwise self._find_and_replace method might corrupt them
        # print("date_string : ",date_string)
        try:
            as_dt = parser.parse(
                date_string,
                default=self.base_date,
                dayfirst=self.dayfirst,
                yearfirst=self.yearfirst,
            )
        except (ValueError, OverflowError):
            # replace tokens that are problematic for dateutil
            date_string, tz_string = self._find_and_replace(date_string, captures)

            ## One last sweep after removing
            date_string = date_string.strip(STRIP_CHARS)
            ## Match strings must be at least 3 characters long
            ## < 3 tends to be garbage
            if len(date_string) < 3:
                return None

            try:
                logger.debug("Parsing {0} with dateutil".format(date_string))
                as_dt = parser.parse(
                    date_string,
                    default=self.base_date,
                    dayfirst=self.dayfirst,
                    yearfirst=self.yearfirst,
                )
            except Exception as e:
                logger.debug(e)
                as_dt = None
            if tz_string:
                as_dt = self._add_tzinfo(as_dt, tz_string)
        return as_dt

    def extract_date_strings(self, text, strict=False):
        """
        Scans text for possible datetime strings and extracts them
        :param strict: Strict mode will only return dates sourced with day, month, and year
        """
        return self.extract_date_strings_inner(text, text_start=0, strict=strict)

    
    
    
    def extract_date_strings_inner(self, text, text_start=0, strict=False):
        """
        Extends extract_date_strings by text_start parameter: used in recursive calls to
        store true text coordinates in output
        """

        # Try to find ranges first
        rng = self.split_date_range(text)
        #print("ranges : ", rng)
        if rng and len(rng) > 1:
            range_strings = []
            for range_str in rng:
                range_strings.extend(
                    self.extract_date_strings_inner(
                        range_str[0], text_start=range_str[1][0], strict=strict
                    )
                )
            #print("range_strings: ",range_strings)
            for range_string in range_strings:
                yield range_string
            return
        
        tokens = self.tokenize_string(text)

        # print("tokens: " , tokens)
        items = self.merge_tokens(tokens)

        #print("items: ", items)
        for match in items:
            #print("match: ", match)

            match_str = match.match_str

            indices = (match.indices[0] + text_start, match.indices[1] + text_start)

            ## Get individual group matches
            captures = match.captures
            # time = captures.get('time')
            digits = captures.get("digits")
            # digits_modifiers = captures.get('digits_modifiers')
            # days = captures.get('days')
            months = captures.get("months")
            years = captures.get("years")
            # timezones = captures.get('timezones')
            # delimiters = captures.get('delimiters')
            # time_periods = captures.get('time_periods')
            # extra_tokens = captures.get('extra_tokens')

            if strict:
                complete = False
                if len(digits) == 3:  # 12-05-2015
                    complete = True
                elif (len(months) == 1) and (len(digits) == 2):  # 19 February 2013 year 09:10
                    complete = True
                elif (len(months) == 1) and (len(digits) == 1):  # 19 February 
                    complete = True
                elif (len(months) == 1) and (len(years) == 1):  # 2022 February 
                    complete = True
                elif (len(years) == 1) and (len(digits) == 2):  # 09/06/2018
                    complete = True

                elif ((len(years) == 1) and (len(months) == 1) and (len(digits) == 1)):  # '19th day of May, 2015'
                    complete = True

                if not complete:
                    #print("No complete format")
                    continue

            ## sanitize date string
            ## replace unhelpful whitespace characters with single whitespace
            match_str = re.sub(r"[\n\t\s\xa0]+", " ", match_str)
            # print("match_str: ", list(match_str))
            
            match_str = match_str.strip(STRIP_CHARS)
            
            #print("match_str_strip: ", list(match_str))
            # Save sanitized source string
            yield match_str, indices, captures

    def tokenize_string(self, text):
        """
        Get matches from source text. Method merge_tokens will later compose
        potential date strings out of these matches.
        :param text: source text like 'the big fight at 2p.m. mountain standard time on ufc.com'
        :return: [(match_text, match_group, {match.capturesdict()}), ...]
        """
        items = []
        
        split_text = text.split(' ')
        
        last_index = 0
        
        #print(text)
        for match in DATE_REGEX.finditer(text):
            flag_valid = True
            match_str = match.group(0)
            # print("match_str: ", match_str)

            indices = match.span(0)
            #print("indices: ", indices)

            captures = match.capturesdict()
            
            group = self.get_token_group(captures)
            
            for item in split_text:
                # print( match_str," -> ",item)
                if match_str in item  and match_str != item and  (match_str.isdigit() is False  and item.isdigit() is False):
                    # print("set '' {} by substring")
                    group = ''
                    captures = {}
            
            if match_str.isdigit():
                match_int = int(match_str)

                if len(match_str) == 2:
                    if match_int > 31:
                        # print("set '' {} by len(2)  match_int > 31")
                        group = ''
                        captures = {}
                        
                if len(match_str) == 3:
                    if match_int != 202:
                        # print("set '' {} by len(3)  !=  202")
                        group = ''
                        captures = {}
            
            
            if indices[0] > last_index :
                # print("set '' {} indices[0] > last_index")
                items.append((text[last_index : indices[0]], "", {}))
                
            items.append((match_str, group, captures))
            last_index = indices[1]
            
            
        if last_index < len(text):
            # print("set '' {} last_index < len(text)")
            items.append((text[last_index : len(text)], "", {}))
            
        return items
    
    

    def stack_delimiters(self,tokens):
        delimiters_list =[]
        
        for idx,token in enumerate(tokens):
            if 'delimiters' in token[2]:
                if len(token[2]['delimiters']) != 0:
                    delimiters_list.append((token[2]['delimiters'][0],idx))
                else : 
                    continue 
                    
            else : delimiters_list.append(('no_group',idx))
        
        return delimiters_list
                                           
    def find_delimiter(self, stack_delimit,start_index, current_index):
        
        return [tupla[0] for tupla in stack_delimit if tupla[1] > start_index and tupla[1] <= current_index ]
                                           
                                           
    def find_next_delimiters(self,tokens):
        
        for token in tokens:
            if 'delimiters' in token[2]:
                if len(token[2]['delimiters']) != 0:
                    return token[2]['delimiters'][0]
                else : continue 
            else : return 'no_group'
        
        
        
                                           

        
            
    def merge_tokens(self, tokens):
        """
        Makes potential date strings out of matches, got from tokenize_string method.
        :param tokens: [(match_text, match_group, {match.capturesdict()}), ...]
        :return: potential date strings
        """
        MIN_MATCHES = 3
        fragments = []
        frag = DateFragment()
        start_index = 0
        last_delimiter = None
        current_is_delimiter = None
        next_delimiter = None
        num_tokens = len(tokens)
        start_char, total_chars = 0, 0
        stack_delim = self.stack_delimiters(tokens)
                                           
        for idx,token in enumerate(tokens):

            total_chars += len(token[0])
            # print("--------------------------<token>")
            
            
            tok_text, group, tok_capts = token[0], token[1], token[2]
            # print("token: ",tok_text, "grupo: ",group )
            
            # si no tiene grupo se reinicia frag 
            if not group:
                if frag.indices[1] > 0:
                    if frag.get_captures_count() >= MIN_MATCHES:
                        fragments.append(frag)
                frag = DateFragment()
                last_delimiter = 'no_group'
                start_index = idx +1
                start_char = total_chars
                # print("-----------------------<break no group>")
                continue
            
            
                
            # print("last delimiter: ", last_delimiter)

            if len(tok_capts['delimiters']) != 0:
                current_is_delimiter = True
                
                
                if idx + 1 <= num_tokens:
                    next_delimiter = self.find_next_delimiters(tokens[idx + 1:])
                    # print("next_delimiter: ", next_delimiter)

                    if next_delimiter is None :
                        next_delimiter = tok_capts['delimiters'][0]
                        # print("-----------------------<no hay delimiter >")
                        

                else: 
                    next_delimiter = tok_capts['delimiters'][0]
                    # print("-----------------------<delimiter $>")
                
                
                delimiters_list = self.find_delimiter(stack_delim, start_index,idx)
                # print("delimiters_list: ",delimiters_list)
                
                num_rep = delimiters_list.count(tok_capts['delimiters'][0])
                
                # print("num_rep:", num_rep)
                sentence_2 = (tok_capts['delimiters'][0] != next_delimiter )
                
                
                if sentence_2 and  num_rep != 2:
                    if frag.indices[1] > 0:
                        if frag.get_captures_count() >= MIN_MATCHES:
                            fragments.append(frag)
    
                    # print("-----------------------<break sentence and num_rep>")
                    frag = DateFragment()
                    last_delimiter = tok_capts['delimiters'][0]
                    start_index = idx +1
                    start_char = total_chars
                    continue
                
                last_delimiter = tok_capts['delimiters'][0]

            
            if frag.indices[1] == 0:
                frag.indices = (start_char, total_chars)
            else:
                frag.indices = (frag.indices[0], total_chars)  # -1

            frag.match_str += tok_text

            for capt in tok_capts:
                if capt in frag.captures:
                    frag.captures[capt] += tok_capts[capt]
                else:
                    frag.captures[capt] = tok_capts[capt]
                

            # print('frag actual: ',frag.match_str)
            start_char = total_chars
            
            # print("--------------------------------<token fin>\n\n")
                
            
            

        if frag.get_captures_count() >= MIN_MATCHES:  # frag.matches
            fragments.append(frag)

        for frag in fragments:
            for gr in ALL_GROUPS:
                if gr not in frag.captures:
                    frag.captures[gr] = []

        return fragments

    @staticmethod
    def get_token_group(captures):
        for gr in ALL_GROUPS:
            lst = captures.get(gr)
            if lst and len(lst) > 0:
                return gr
        return ""

    @staticmethod
    def split_date_range(text):
        st_matches = RANGE_SPLIT_REGEX.finditer(text)
        start = 0
        parts = []  # List[Tuple[str, Tuple[int, int]]]

        for match in st_matches:
            match_start = match.start()
            if match_start > start:
                parts.append((text[start:match_start], (start, match_start)))
            start = match.end()

        if start < len(text):
            parts.append((text[start:], (start, len(text))))

        return parts


def find_dates(text, source=True, index=True, strict=False, base_date=None, first="month"):
    """
    Extract datetime strings from text

    :param text:
        A string that contains one or more natural language or literal
        datetime strings
    :type text: str|unicode
    :param source:
        Return the original string segment
    :type source: boolean
    :param index:
        Return the indices where the datetime string was located in text
    :type index: boolean
    :param strict:
        Only return datetimes with complete date information. For example:
        `July 2016` of `Monday` will not return datetimes.
        `May 16, 2015` will return datetimes.
    :type strict: boolean
    :param base_date:
        Set a default base datetime when parsing incomplete dates
    :type base_date: datetime
    :param first:
        Whether to interpret the the first value in an ambiguous 3-integer date
        (01/02/03) as the month, day, or year. Values can be `month`, `day`, `year`.
        Default is `month`.
    :type first: str|unicode


    :return: Returns a generator that produces :mod:`datetime.datetime` objects,
        or a tuple with the source text and index, if requested
    """
    date_finder = DateFinder(base_date=base_date, first=first)
    return date_finder.find_dates(text, source=source, index=index, strict=strict)
