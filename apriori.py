"""
frequent_items: a set of items where
"""
import itertools


class Basket(object):
    def __init__(self, items: list, basket_name=None):
        self.items = set(frozenset([item]) for item in items)
        self.index = None
        self.basket_name = basket_name

    def __add__(self, other):
        if isinstance(other, BasketSet):
            other.add_basket(self)
            return other
        elif isinstance(other, Basket):
            basket_set = BasketSet()
            basket_set.add_basket(self)
            basket_set.add_basket(other)
            return basket_set


class BasketSet(object):
    def __init__(self, *baskets):
        self.baskets = dict()  # {index: basket}
        self.item_table = dict()  # {frozenset({item}): {basket_index_1, basket_index_2, ...}}

        self.frequent_item_sets = dict()  # {level: set()}

        for basket in baskets:
            self.add_basket(basket)

        self.minimum_support = None
        self.minimum_confidence = None

    def set_min_support_confidence(self, minimum_support, minimum_confidence):
        self.minimum_support = minimum_support
        self.minimum_confidence = minimum_confidence

    def add_basket(self, basket):
        if self.baskets:
            basket_index = max(list(self.baskets.keys())) + 1
        else:
            basket_index = 1

        basket.index = basket_index
        self.baskets[basket_index] = basket
        self._add_items(basket.items, basket_index)

    def _add_items(self, items, basket_index):
        for item in items:
            if item in self.item_table:
                self.item_table[item].add(basket_index)
            else:
                self.item_table[item] = {basket_index}

    def remove_basket(self, basket):
        self._remove_items(basket.items, basket.index)
        del self.baskets[basket.index]

    def _remove_items(self, items, basket_index):
        for item in items:
            if item in self.item_table:
                self.item_table[item].remove(basket_index)

    def __add__(self, other):
        new_basket_set = BasketSet()
        if isinstance(other, BasketSet):
            for basket_index, basket in other.baskets.items():
                new_basket_set.add_basket(basket)
            return new_basket_set

        elif isinstance(other, Basket):
            self.add_basket(other)
            return self

    def look_up_baskets_by_items(self, items):
        # find intersection of item_table by items:
        intersected_basket = set.intersection(*[self.item_table[frozenset([item])] for item in items])
        return intersected_basket

    @staticmethod
    def _build_join_set(item_sets):
        joined_set = set()
        for item_set in item_sets:
            joined_set.update(item_set)

        return joined_set

    @staticmethod
    def _get_k_candidate_item_sets(joined_set, set_size):
        candidate_item_sets = set(frozenset(subset) for subset in itertools.combinations(joined_set, set_size))
        return candidate_item_sets

    def build_frequent_item_sets(self, level):
        if level == 1:
            frequent_item_set = set()
            join_set = BasketSet._build_join_set(self.item_table.keys())
            candidate_item_sets = BasketSet._get_k_candidate_item_sets(join_set, set_size=1)

            for candidate_item_set in candidate_item_sets:
                if len(self.item_table[candidate_item_set]) / len(self.baskets) >= self.minimum_support:
                    frequent_item_set.add(candidate_item_set)
            self.frequent_item_sets[level] = frequent_item_set
        else:
            while (level - 1) not in self.frequent_item_sets:
                if level - 1 == 1:
                    self.build_frequent_item_sets(1)
                else:
                    self.build_frequent_item_sets(level - 2 + 1)
            else:
                frequent_item_set = set()
                join_set = BasketSet._build_join_set(self.frequent_item_sets[level-1])
                candidate_item_sets = BasketSet._get_k_candidate_item_sets(join_set,
                                                                           set_size=level)

                # Apriori property: any subset of the frequent_item_set is also a frequent_item_set:
                for candidate_item_set in candidate_item_sets:
                    sub_candidate_item_sets = BasketSet._get_k_candidate_item_sets(candidate_item_set,
                                                                                   set_size=level-1)

                    apriori_condition_on_proper_subset = all([True for sub_candidate_item_set in sub_candidate_item_sets
                        if sub_candidate_item_set in self.frequent_item_sets[level-1]])

                    apriori_condition_on_its_own_set = len(self.look_up_baskets_by_items(candidate_item_set)) \
                                                       / len(self.baskets) >= self.minimum_support

                    if apriori_condition_on_its_own_set and apriori_condition_on_proper_subset:
                        frequent_item_set.add(candidate_item_set)

                self.frequent_item_sets[level] = frequent_item_set







basket_items_1 = ['milk', 'sugar', 'bread', 'coke', 'corn', 'carrot', 'fish', 'chicken', 'beef', 'lamb', 'lettuces', 'suassages', 'egg']
basket_items_2 = ['milk', 'sugar', 'bread', 'corn', 'beef', 'lettuces']
basket_items_3 = ['milk', 'sugar','fish']
basket_items_4 = ['milk', 'sugar', 'bread', 'corn', 'beef', 'egg']
basket_items_5 = ['milk', 'sugar','corn']
basket_items_6 = ['milk', 'sugar', 'corn', 'beef', 'egg']
basket_items_7 = ['milk', 'fish']

basket_set = Basket(basket_items_1) + Basket(basket_items_2) + Basket(basket_items_3) + Basket(basket_items_4) + Basket(basket_items_5) + Basket(basket_items_6)  + Basket(basket_items_7)
basket_set.minimum_support = 0.5
basket_set.build_frequent_item_sets(level=4)

print(basket_set.frequent_item_sets[4])