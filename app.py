import ruamel.yaml
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


GH_TOKEN = "<enter your github token here>"


def re_merge_content(item, values, filed_1, field_2, found_axes_entry, index, counter, axes):
    if values[index + 1] != field_2:
        axes_index = index

    if item == filed_1 or found_axes_entry:
        counter += 1

        found_axes_entry = True
        axes.append(values[axes_index+counter])

    if values[axes_index + counter + 1] == field_2:
        found_axes_entry = False

        item = "\n".join(axes)
    return


def yaml_builder(input_txt, out_yaml):
    values = []
    document = dict()
    # particular_fields = [
    #     'ID', 'Description', 'Project purpose', 'Target Platform',
    #     'Preferred Method', 'Cell type', 'Access control',
    #     'Responsible', 'Data Source', 'Data Preprocessing', 'Quality Control',
    #     'Documents & publications', 'License', 'Ownership', 'Personal Data',
    #     'Additional Information']
    list_fields = ['APIs', 'Null values', '(Meta) data Standards']

    var_lettura = input_txt.splitlines()
    found_axes_entry = False
    counter = 0
    axes = []
    for index, i in enumerate(var_lettura):

        if i != "\n" and i != '':

            st = i.strip("\n")
            st = st.strip(" ")
            st = st.replace("'", "")
            # if st == '### Axes':
            #     breakpoint()
            #     re_merge_content(st, var_lettura, '### Axes', '### Cell type', found_axes_entry, index, counter, axes)
            # elif st == '### Description':

            #     re_merge_content(st, var_lettura, '### Description', '### Project purpose2', found_axes_entry, index, counter, axes)

            # elif not found_axes_entry:
            #     counter = 0
            #     axes = []
            #     values.append(st)
            if st == '### Axes':
                axes_index = index

            if st == '### Axes' or found_axes_entry:
                counter += 1

                found_axes_entry = True
                axes.append(var_lettura[axes_index+counter])

                if var_lettura[axes_index + counter + 1] == '### Cell type':
                    found_axes_entry = False

                    st = axes
            if not found_axes_entry or st == '### Axes':
                values.append(st)

    for i in range(0, len(values)-1, 2):
        field = values[i]
        if type(values[i]) == str and values[i].startswith('### '):
            field = values[i][4:]

        val = values[i+1]
        if val == '_No response_':
            continue

        if field in list_fields:
            list_value = val.strip(" ").split(", ")
            document[field] = list_value
        elif type(val) == str:

            document[field] = val.strip(" ")
        else:
            document[field] = val
    with open(out_yaml, 'w') as file:
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=3, offset=3)
        documents = yaml.dump(document, file)
    file.close()


transport = RequestsHTTPTransport(
    url="https://api.github.com/graphql",
    headers={'Authorization': 'token ' + GH_TOKEN})

client = Client(transport=transport)

query_1 = gql(
        """
        query  {
            organization(login: \"FAIRiCUBE\") {
                repository(name: "data-requests") {
                    issues(last:100, states:OPEN) {
                        edges {
                            node {
                            title
                            body
                            }
                        }
                        }
                    }
                }
            }
        """
    )

issues = client.execute(query_1)['organization']['repository']['issues']['edges']
for index, issue in enumerate(issues):
    title = issue['node']['title'].split("]: ")[-1]
    yaml_builder(issue['node']['body'], f'{title}.yaml')
