param_good_case_insensitive_false = [("abbbccdf", 3),
                                     ("aderffs!", 6),
                                     ("aaaabccc", 1),
                                     ("aaAAaa", 0),
                                     ("aaAAbcBcC", 3),
                                     ("", 0),
                                     ]

param_good_case_insensitive_true = [("aaAaa", 0),
                                    ("aAbBcCd", 1),
                                    ("a!!+-+Ab", 2),
                                    ("", 0),
                                    ]

param_with_typeerror = [(["Aaaf"]),
                        (123, ),
                        (33.12, ),
                        ({"key": "value"}, ),
                        ]

param_for_cache = [("aaBBaa", 1),
                   ("bbAAbb", 1),
                   ("aaBBaa", 0),
                   ("aaaaaB", 1),
                   ("bbAAbb", 0),
                   ]
