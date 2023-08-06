from django.test import TestCase
from querylanguage import Parser, exceptions
from .models import MainModel, RelatedModel, RelatedOfRelatedModel
from django.db.models import Q, F
import random


class BaseTest(TestCase):
    def setUp(self):
        # populate database
        nrows = 1000
        random.seed(a=243)
        for i in range(nrows):
            s = ['bla', 'Bla', 'foo', 'bar', 'Bar', 'Rab', 'Abr', 'abc', 'cAb', 'foo bar']
            ro = RelatedOfRelatedModel.objects.create(rr_c1=random.choice(s),
                                                      rr_f1=random.randrange(-5, 5),
                                                      rr_f2=(random.random() - 0.5) * 50,
                                                      rr_f3=(random.random() - 0.5) * 10)
            r = RelatedModel.objects.create(r_c1=random.choice(s),
                                            r_f1=random.randrange(-5, 5),
                                            r_f2=(random.random() - 0.5) * 50,
                                            r_f3=(random.random() - 0.5) * 10,
                                            r_related=ro)
            m = MainModel.objects.create(c1=random.choice(s),
                                        f1=random.randrange(-5, 5),
                                        f2=(random.random() - 0.5) * 50,
                                        f3=(random.random() - 0.5) * 10,
                                        related=r)
        self.parser = Parser(MainModel)

    def parse(self, query):
        return self.parser.parse(query)


class BasicTest(BaseTest):

    def test_number(self):
        flt = self.parse("f1 = 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1=1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_number_float(self):
        flt = self.parse("f1 = 1.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1=1.0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_gt(self):
        flt = self.parse("f1 > 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__gt=1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_gte(self):
        flt = self.parse("f1 >= 1.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__gte=1.0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_lt(self):
        flt = self.parse("f2 < 1.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f2__lt=1.0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_lt_exp(self):
        flt = self.parse("f2 < 1e1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f2__lt=1e1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_lt_exp(self):
        flt = self.parse("f2 < 1.5e1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f2__lt=1.5e1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_lte(self):
        flt = self.parse("f1 <= 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__lte=1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_like_int(self):
        flt = self.parse("f1 ~ 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__icontains=1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_like_float(self):
        flt = self.parse("f2 ~ 1.")
        qs = MainModel.objects.filter(flt)
        # import ipdb; ipdb.set_trace()
        ref = MainModel.objects.filter(f2__icontains=1.0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_like_neg(self):
        flt = self.parse("f1 ~ -1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__icontains=-1)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_like_charfield(self):
        flt = self.parse("c1 ~ 'ar'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1__icontains='ar')
        self.assertNotEqual(qs.count(), 0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_basic_comparison_ne(self):
        flt = self.parse("f1 != 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(~Q(f1=1))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_operator_in(self):
        flt = self.parse("f1 in (0,1, -2)")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__in=(0, 1, -2))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_operator_not_in(self):
        flt = self.parse("f1 NOT in (0, 1 , -2)")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(~Q(f1__in=(0, 1, -2)))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_operator_not_in_charfield(self):
        flt = self.parse("c1 In ('foo', 'Bar')")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1__in=('foo', 'Bar', 'e'))
        self.assertNotEqual(qs.count(), 0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_single_string_single_quote(self):
        flt = self.parse("c1 = 'foo'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1='foo')
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_single_string_double_quote(self):
        flt = self.parse('c1 = "foo"')
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1='foo')
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_phrase_single_quote(self):
        flt = self.parse("c1 = 'foo bar'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1='foo bar')
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_phrase_double_quote(self):
        flt = self.parse('c1 = "foo bar"')
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(c1='foo bar')
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_is_null(self):
        flt = self.parse('f1 is null')
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__isnull=True)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_is_not_null(self):
        flt = self.parse('f1 IS NOT null')
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(f1__isnull=False)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)


class RelatedModelTest(BaseTest):

    def test_dot(self):
        flt = self.parse("related.r_c1 = 'foo'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(related__r_c1="foo")
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_nested_fields(self):
        flt = self.parse("related.r_related.rr_c1 = 'Bar'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(related__r_related__rr_c1="Bar")
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_nested_fields_double_underscore(self):
        flt = self.parse("related.r_related.rr_c1 = 'Bar'")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(related__r_related__rr_c1="Bar")
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_between(self):
        flt = self.parse("related.r_f1 between -1 and 1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(Q(related__r_f1__gte=-1) & Q(related__r_f1__lte=1))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_in(self):
        flt = self.parse("related.r_related.rr_f1 in (1, 2, 3)")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(related__r_related__rr_f1__in=[1, 2, 3])
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)


class MathTest(BaseTest):

    def test_sub(self):
        flt = self.parse("f2 - f3 >= 1.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=F('f2') - F('f3')).filter(expr__gte=1.0)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_addsub(self):
        flt = self.parse("f1+f2 - f3 < 3")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=F('f1') + F('f2') - F('f3')).filter(expr__lt=3)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_paren(self):
        flt = self.parse("f1 - (f2 + f3) / f1 > 3.14")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=F('f1') - (F('f2') + F('f3')) / F('f1')).filter(expr__gt=3.14)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_paren_many(self):
        flt = self.parse("((f2 - f1)) / f1 > 1e2 - 105")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=((F('f2') - F('f1'))) / F('f1')).filter(expr__gt=1e2 - 105)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_paren_related(self):
        flt = self.parse("2*(f1 - f2) / related.r_f3 + related.r_related.rr_f2 > -3.4")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=2*(F('f1')-F('f2'))/F('related__r_f3') + F('related__r_related__rr_f2')).filter(expr__gt=-3.4)
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_both_side_simple_stupid(self):
        flt = self.parse("f1 - f2 = -(f2 - f1)*1.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr1=F('f1')-F('f2'), expr2=-(F('f2')-F('f1'))*1.0).filter(expr1=F('expr2'))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_both_side_simple(self):
        flt = self.parse("f1 + 2.123 != related.r_f1 + 2.123")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr1=F('f1')+2.123, expr2=F('related__r_f1')+2.123).filter(~Q(expr1=F('expr2')))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_both_side_complex(self):
        flt = self.parse("f1 - f2 / related.r_f3 != f2 - related.r_f1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr1=F('f1')-F('f2')/F('related__r_f3'), expr2=F('f2') - F('related__r_f1')).filter(~Q(expr1=F('expr2')))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_expr_in(self):
        flt = self.parse("f1 - related.r_f1 + related.r_related.rr_f1 in (1,2,0)")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=F('f1')-F('related__r_f1')+F('related__r_related__rr_f1')).filter(expr__in=[1, 2, 0])
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_expr_between(self):
        flt = self.parse("0.5*f1 between f2 and 2*f2")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.annotate(expr=0.5*F('f1')).filter(Q(expr__gte=F('f2')) & Q(expr__lte=2*F('f2')))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)


class LogicalTest(BaseTest):

    def test_or(self):
        flt = self.parse("f1 =0.0 OR f3 < +0.1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(Q(f1=0.0) | Q(f3__lte=0.1))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_and(self):
        flt = self.parse("f3 < -0.1 aNd f1 = -0.0")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(Q(f3__lt=-0.1) & Q(f1=0.0))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_and_or(self):
        flt = self.parse("f3 < -0.1 aNd f1 = -0.0 or f2 >= -0.1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(Q(f3__lt=-0.1) & Q(f1=0.0) | Q(f2__gte=-0.1))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_and_or_paren(self):
        flt = self.parse("(f3 < -0.1 AND f1 = -0.0) OR f2 >= -0.1")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter((Q(f3__lt=-0.1) & Q(f1=0.0)) | Q(f2__gte=-0.1))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)

    def test_and_or_paren2(self):
        flt = self.parse("f3 < -0.1 aNd (f1 = -0.0 oR f2 >= -0.1)")
        qs = MainModel.objects.filter(flt)
        ref = MainModel.objects.filter(Q(f3__lt=-0.1) & (Q(f1=0.0) | Q(f2__gte=-0.1)))
        print("\nqs.count()--->", qs.count())
        print("ref.count()--->", ref.count())
        self.assertEqual(qs.count(), ref.count())
        self.assertNotEqual(qs.count(), 0)
        self.assertQuerySetEqual(qs, ref, ordered=False)


class ValidationTest(BaseTest):

    def test_field_must_exist_in_model(self):
        # Use field that is not present on MainModel
        try:
            self.parse("unknown > 10")
        except exceptions.FieldDoesNotExist as e:
            self.assertEqual(e.field, 'unknown')
        else:
            self.fail("Unknown field shouldn't be accepted")
