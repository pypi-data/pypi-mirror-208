import type { IDataSourceProps } from "../interfaces";
import type { IRow } from "@kanaries/graphic-walker/dist/interfaces";
export declare function loadDataSource(props: IDataSourceProps): Promise<IRow[]>;
