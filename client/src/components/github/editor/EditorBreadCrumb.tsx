import React from "react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "../../ui/breadcrumb";
import { getFileIcon } from "../directory/fileIcons";

interface EditorBreadCrumbProps {
  filePath: string;
}

const EditorBreadCrumb: React.FC<EditorBreadCrumbProps> = ({ filePath }) => {
  const pathSegments = filePath.split("/");
  return (
    <Breadcrumb className="p-2">
      <BreadcrumbList>
        {pathSegments.map((item, index) => (
          <React.Fragment key={`${item}-${index}`}>
            <BreadcrumbItem>
              <div className="flex items-center gap-1">
                {index === pathSegments.length - 1 && getFileIcon(item)}
                <span className="text-xs font-medium">{item}</span>
              </div>
            </BreadcrumbItem>
            {index < pathSegments.length - 1 && <BreadcrumbSeparator />}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

export default EditorBreadCrumb;
