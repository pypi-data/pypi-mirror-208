class QuestionTypes:
    geo = 1
    text = 2
    number = 3
    option = 4
    multiple_option = 5
    photo = 6
    date = 7

    FieldStr = {
        geo: 'Geo',
        text: 'Text',
        number: 'Number',
        option: 'Option',
        multiple_option: 'Multiple_Option',
        photo: 'Photo',
        date: 'Date',
    }


class StatusTypes:
    draft = 1
    submitted = 2
