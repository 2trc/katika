from django.test import TestCase
from django.contrib.postgres.search import SearchQuery
from django.db.models import Q

from tender.management.commands.check_contribuables import compose_number_query, compose_text_query, compose_query


class TestCheckContribuables(TestCase):

    def test_compose_text_query(self):

        text = "some name"

        a = str(compose_text_query(text))
        b = str(Q(change_list__search_vector=SearchQuery(text, config='french_unaccent')))

        self.assertEqual(a, b)
    

    def test_compose_number_query(self):

        bp = "54321"
        a = str(compose_number_query(bp))
        b = str(
            Q(change_list__search_vector=SearchQuery(bp, config='french_unaccent'))
            |Q(bp__contains=bp)
            )

        self.assertEqual(a, b)
                         
        

        short_phone = "12345678"
        a = str(compose_number_query(short_phone))
        b = str(Q(change_list__search_vector=SearchQuery(short_phone, config='french_unaccent'))|
                Q(telephone__contains=short_phone)
                )
        
        self.assertEqual(a, b)
        
        long_phone = "123456789"
        long_phone_2 = "23456789"
        a = str(compose_number_query(long_phone))
        b = str(
            Q(change_list__search_vector=SearchQuery(long_phone, config='french_unaccent'))            
            |Q(change_list__search_vector=SearchQuery(long_phone_2, config='french_unaccent'))
            |Q(telephone__contains=long_phone_2)                         
        )
        self.assertEqual(a, b)

    
    def test_compose_query(self):

        numbers = "123456789/87654321"

        a = str(Q()|Q()|compose_number_query("123456789")|compose_number_query("87654321"))
        b = str(compose_query(numbers))

        self.assertEqual(a,b)

        name = "Angela Koto"
        phones = "1234567/9099112"
        bp = "1231"
        mixed_input = [name, phones, bp]

        a = str(
            Q()|compose_text_query(name)
            |Q()|Q()|compose_number_query("1234567")|compose_number_query("9099112")
            |compose_number_query(bp))
        b = str(compose_query(mixed_input))

        self.assertEqual(a,b)

        
