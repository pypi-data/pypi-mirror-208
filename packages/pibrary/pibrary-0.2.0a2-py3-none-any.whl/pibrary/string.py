import string
from collections import UserString


class String(UserString):
    """
    This class is used to preprocess a text.
    """

    @property
    def str(self) -> str:
        """Property to get the string of the text.

        Returns:
            str: String of the text.
        """
        return self.data

    def remove_punctuation_except_period(self) -> UserString:
        """
        Remove punctuation except period from a text.

        Returns:
            UserString: Text without punctuation except period.
        """
        # Remove punctuation
        punctuation = string.punctuation.replace(".", "")
        return self.translate(str.maketrans("", "", punctuation))

    def remove_punctuation(self) -> UserString:
        """Remove punctuation from a text.

        Returns:
            UserString: Text without punctuation.
        """
        return self.translate(str.maketrans("", "", string.punctuation))

    def remove_digits(self) -> UserString:
        """
        This function is used to remove digits from a text.

        Returns:
            UserString: Text without digits.
        """
        return self.translate(str.maketrans("", "", string.digits))

    def remove_duplicate_spaces(self) -> UserString:
        """Remove duplicate spaces from a text.

        Returns:
            UserString: Text without duplicate spaces.
        """
        return String(" ".join(self.split()))
