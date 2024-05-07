# brain_agriculture

It consists of a rural producer registration with the following data:

- CPF or CNPJ
- Producer name
- Farm Name
- City
- State
- Total area in hectares of the farm
- Arable area in hectares
- Vegetation area in hectares
- Planted crops (Soybeans, Corn, Cotton, Coffee, Sugarcane)

## Business requirements
- The user must be able to register, edit, and exclude rural producers.
- The system must validate CPF and CNPJ entered incorrectly.
- The sum of arable area and vegetation must not be greater than the total area of the farm
- Each producer can plant more than one crop on their Farm.
- The platform must have an API that returns:
  - Total farms in quantity
  - Total farms in hectares (total area)
  - Pie chart by state.
  - Pie chart by culture.
  - Pie chart by land use (Agricultural area and vegetation)
