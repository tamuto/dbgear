interface Mapping {
  id: string,
  group: string,
  base: string,
  name: string,
  instances: string[],
  description: string,
  deployment: boolean,
  parent: Mapping
}
