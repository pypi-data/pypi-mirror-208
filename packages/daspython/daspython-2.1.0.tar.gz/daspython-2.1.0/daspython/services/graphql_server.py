import json
import requests

from daspython.common.api import ApiMethods


class GraphQLServer(ApiMethods):
    def get_attribute_excel_info(self, attribute_alias):

        data = {
            'query': GET_ATTRIBUTE_EXCEL_INFO,
            'variables': {
                "attributeAlias": attribute_alias,
                "isFileHeader": True	
            },
        }        

        return self.post_grahpql_data(json_data=data)        


GET_ATTRIBUTE_EXCEL_INFO = """
query GetAttributeExcelInfo($attributeAlias: String!, $isFileHeader: Boolean!) {
  attributesInfo(alias: $attributeAlias, isHandleGroupedFields: true) {
    attributes {
      id,
      name,        
      alias,
      entryForm {
          rules
      },        
      entryFields(displayType: input, isFileHeader: $isFileHeader) {
          attributeId,
          column,
          displayName,
          x,
          y,
          description,
          isMandatory,
          inputType,
          displayType,
          isSearchable,
          isClearedOnReuse,
          customData,
          copyFromParent,
          isPrintable,
          isSortable,
          isReadOnly
      }                 
    }
  }
}
"""