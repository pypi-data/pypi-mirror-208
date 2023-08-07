import re 

def arStrip(text , diacs=True , smallDiacs=True , shaddah=True , digit=True, alif=True , specialChars=True ):
    
    """
    This method removes Arabic diacritics, Quranic annotation signs, shaddah, English and Arabic digits, unify alif with hamzah,
    some special characters, spaces, underscore and Arabic tatwelah from the input text.

    Args:
        text (:obj:`str`): Arabic text to be processed.
        diacs (:obj:`bool`): flag to remove Arabic diacretics [ ًٌٍَُِْ] (default is True).
        smallDiacs (:obj:`bool`): flag to remove small Quranic annotation signs (default is True).
        shaddah (:obj:`bool`): flag to remove shaddah (default is True).
        digit (:obj:`bool`): flag to remove English and Arabic digits (default is True).
        alif (:obj:`bool`): flag to unify alif with hamzah (default is True).
        specialChars (:obj:`bool`): flag to remove some special characters (default is True).

    Returns:
        :obj:`str`: processed text with removed diacritics, Quranic annotation signs, shaddah, digits, and special characters.

    **Example:**

    .. highlight:: python
    .. code-block:: python

        from nlptools.utils import parser
        processed_text =parser.arStrip('2023الجو جميلُ' , True , True , True ,  True , False , True )
        print(processed_text)

        #putput
        الجو جميل
    """
    try:
        if text: # if the input string is not empty do the following
            #print("in if")
            if diacs == True :
                text = re.sub(r'[\u064B-\u0650]+', '',text) # Remove all Arabic diacretics [ ًٌٍَُِْ]
                text = re.sub(r'[\u0652]+', '',text) # Remove SUKUN
            if shaddah == True:
                text = re.sub(r'[\u0651]+', '',text) # Remove shddah
            if smallDiacs == True:
                text = re.sub(r'[\u06D6-\u06ED]+', '',text) # Remove all small Quranic annotation signs
            if digit == True:
                text = re.sub('[0-9]+', ' ',text) # Remove English digits
                text = re.sub('[٠-٩]+', ' ',text)# Remove Arabic digits
            
            if alif == True:                             # Unify alif with hamzah: 
                text = re.sub('ٱ', 'ا',text);
                text = re.sub('أ', 'ا',text);
                text = re.sub('إ', 'ا',text);
                text = re.sub('آ', 'ا',text);
            if specialChars == True:
                text = re.sub('[?؟!@#$%-]+' , '' , text) # Remove some of special chars 

            text = re.sub('[\\s]+'," ",text) # Remove all spaces
            text = text.replace("_" , '') #Remove underscore
            text = text.replace("ـ" , '') # Remove Arabic tatwelah
            text = text.strip() # Trim input string
    except:
        return text
    return text
    

# def remove_punctuation(text):
#     """
#     Removes punctuation marks from the input text.
    
#     Args:
#       text (:obj:`str`): The input string containing punctuation marks.
    
#     Returns:
#       :obj:`str`: The output string with all punctuation marks removed.
#     **Example:**

#     .. highlight:: python
#     .. code-block:: python

#         from nlptools.utils import parser
#         return parser.removePunctuation("te!@#،$%%؟st")

#     """
#     outputString = text
#     try:
#         if text:
#             # English Punctuation
#             outputString = re.sub(r'[\u0021-\u002F]+', '',text) # ! " # $ % & ' ( ) * + ,  - . /
#             outputString = re.sub(r'[U+060C]+', '',outputString) # ! " # $ % & ' ( ) * + ,  - . /
#             outputString = re.sub(r'[\u003A-\u0040]+', '',outputString) # : ; < = > ? @ 
#             outputString = re.sub(r'[\u005B-\u0060]+', '',outputString) # [ \ ] ^ _ `
#             outputString = re.sub(r'[\u007B-\u007E]+', '',outputString) # { | } ~
#             # Arabic Punctuation
#             outputString = re.sub(r'[\u060C]+', '',outputString) # ،
#             outputString = re.sub(r'[\u061B]+', '',outputString) # ؛
#             outputString = re.sub(r'[\u061E]+', '',outputString) # ؞
#             outputString = re.sub(r'[\u061F]+', '',outputString) # ؟
#             outputString = re.sub(r'[\u0640]+', '',outputString) # ـ
#             outputString = re.sub(r'[\u0653]+', '',outputString) # ٓ
#             outputString = re.sub(r'[\u065C]+', '',outputString) #  ٬
#             outputString = re.sub(r'[\u066C]+', '',outputString) #  ٜ 
#             outputString = re.sub(r'[\u066A]+', '',outputString) # ٪
#             outputString = re.sub(r'["}"]+', '',outputString) 
#             outputString = re.sub(r'["{"]+', '',outputString) 
#     except:
#         return text

#     return outputString

def remove_punctuation(text):
    """
    Removes punctuation marks from the text.
    
    Args:
      text (:obj:`str`): The text containing punctuation marks.
    
    Returns:
      :obj:`str`: The output text with all punctuation marks removed.

    **Example:**

    .. highlight:: python
    .. code-block:: python
    
        from nlptools.utils import parser
        return parser.remove_punctuation("te!@#،$%%؟st")

        #output
        test
    """
    try:
        if text:
            punctuation_marks = [r'[\u0021-\u002F]+', r'[U+060C]+', r'[\u003A-\u0040]+',
                                 r'[\u005B-\u0060]+', r'[\u007B-\u007E]+', r'[\u060C]+',
                                 r'[\u061B]+', r'[\u061E]+', r'[\u061F]+', r'[\u0640]+',
                                 r'[\u0653]+', r'[\u065C]+', r'[\u066C]+', r'[\u066A]+',
                                 r'["}"]+', r'["{"]+']
            outputString = text
            for punctuation in punctuation_marks:
                outputString = re.sub(punctuation, '', outputString)
    except:
        return text
    return outputString

# def removeEnglish( text ):
#     """
#     Removes all Latin characters from the text.

#     Args:
#         text (:obj:`str`): The text to remove Latin characters from.

#     Returns:
#          outputString (:obj:`str`): The text with all Latin characters removed.
#     Note:
#         If an error occurs during processing, the original text is returned.
#     **Example:**

#     .. highlight:: python
#     .. code-block:: python
    
#         from nlptools.utils import parser
#         return parser.removePunctuation("te!@#،$%%؟st")
#         return parser.removeEnglish("miojkdujhvaj1546545spkdpoqfoiehwv nWEQFGWERHERTJETAWIKUYFC")
#     """
#     try:
#         if text:
#             text = re.sub('[a-zA-Z]+', ' ',text)
#     except:
#         return text
#     return text

def remove_latin(text):
    """
    This method removes all Latin characters from the input text.

    Args:
        text (:obj:`str`): The text to remove Latin characters from.

    Returns:
         outputString (:obj:`str`): The text with all Latin characters removed.
    Note:
        If an error occurs during processing, the original text is returned.
    **Example:**

    .. highlight:: python
    .. code-block:: python

        from nlptools.utils import parser
        return parser.remove_latin("miojkdujhvaj1546545spkdpoqfoiehwv nWEQFGWERHERTJETAWIKUYFC")

        #output
        1546545   
    """
    try:
        if text:
            text = re.sub('[a-zA-Z]+', ' ', text)
    except:
        return text
    return text


