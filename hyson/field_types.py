
FIELD_TYPES = {
    'BigIntegerField': 'int',
    'SmallIntegerField': 'int',
    'PositiveIntegerField': 'int',
    'PositiveSmallIntegerField': 'int',
    'ManyToManyField': 'string', # TODO: no idea
    'ForeignKey': 'int',
    'CharField': 'string',
    'TextField': 'string',
    'BooleanField': 'bool',
    'AutoField': 'string', # TODO: no idea
    'DateTimeField': 'date',
    'RelatedObject': 'int',
    'EmailField': 'string',
    'FileField': 'string',
    'ImageField': 'string',
    'ImageWithThumbnailsField': 'string', # sorl
    'FloatField': 'float'
}


COLUMN_TYPES = {
    'BigIntegerField': 'numbercolumn',
    'SmallIntegerField': 'numbercolumn',
    'PositiveIntegerField': 'numbercolumn',
    'PositiveSmallIntegerField': 'numbercolumn',
    'ManyToManyField': None,
    'ForeignKey': 'numbercolumn',
    'CharField': None,
    'TextField': None,
    'BooleanField': 'booleancolumn',
    'AutoField': None,
    'DateTimeField': 'datecolumn',
    'RelatedObject': 'numbercolumn',
    'EmailField': None,
    'FileField': None,
    'ImageField': None,
    'ImageWithThumbnailsField': None,
    'FloatField': 'numbercolumn'
}

COLUMN_FORMATS = {
    'ForeignKey': '0'
}