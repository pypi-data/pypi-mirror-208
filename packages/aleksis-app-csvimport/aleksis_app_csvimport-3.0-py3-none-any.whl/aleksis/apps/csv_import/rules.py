from rules import add_perm

from aleksis.core.util.predicates import has_global_perm, has_person

import_data_predicate = has_person & has_global_perm("csv_import.import_data")
add_perm("csv_import.import_data_rule", import_data_predicate)

view_importtemplate_predicate = has_person & has_global_perm("csv_import.view_importtemplate")
add_perm("csv_import.view_importtemplate_rule", view_importtemplate_predicate)

upload_importtemplate_predicate = has_person & (
    has_global_perm("csv_import.add_importtemplate")
    | has_global_perm("csv_import.change_importtemplate")
)
add_perm("csv_import.upload_importtemplate_rule", upload_importtemplate_predicate)

view_csv_menu_predicate = (
    import_data_predicate | view_importtemplate_predicate | upload_importtemplate_predicate
)
add_perm("csv_import.view_csv_menu_rule", view_csv_menu_predicate)
