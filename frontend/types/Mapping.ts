interface Mapping {
  id: string,
  base: string,
  name: string,
  instances: string[],
  description: string,
  deployment: boolean,
  parent: Mapping
}
